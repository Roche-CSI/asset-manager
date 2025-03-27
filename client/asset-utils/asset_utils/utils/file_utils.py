import asyncio
import base64
import difflib
import hashlib
import io
import json
import mimetypes
import os
import resource
import shutil
import subprocess
import zipfile
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Union

import aiofiles
import crcmod
import psutil
import yaml
from ruamel.yaml import YAML

from asset_utils.common.exceptions import AssetException
from .file_html_diff import FileHtmlDiff
from .file_tree import TreeNode
from .log_utils import LoggingMixin
from .stat_utils import stat2dict
from .utils import list_files, remove_suffix
from .utils import make_dirs, batch


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


"""extra mimetypes not yet added to mimetypes library"""
EXTRA_MIMES = {
    'application/x-yaml': ['.yaml', '.yml'],
    'application/x-hdf5': ['.h5']
}


class FileUtils(LoggingMixin):

    @staticmethod
    def mime_type(src) -> str:
        """detect the mimetype of a file given its path"""
        mime = mimetypes.guess_type(src)
        if mime and len(mime) > 1:
            mime = mime[0]
        # mimetypes doesn't work for yaml since
        # yaml is not yet in the IANA registry, so we need to manually plug it
        if not mime:
            mime = FileUtils._extra_mime(src)
        return mime

    @staticmethod
    def _extra_mime(path):
        """find mimetypes for files that are not yet defined in the mimetypes lib"""
        filename, extension = os.path.splitext(path)
        for mime in EXTRA_MIMES:
            exts = EXTRA_MIMES[mime]
            if extension in exts:
                return mime
        return None

    @staticmethod
    def read_file_mime_type(path: str, mime_type):
        if mime_type == 'application/json':
            return FileUtils.read_json(path)
        elif mime_type == 'application/x-yaml':
            return FileUtils.read_yaml(path)
        elif mime_type == 'text/plain':
            return FileUtils.read_text(path)
        else:
            raise Exception(f"unsupported mime type {mime_type}")

    @staticmethod
    def read_yaml_with_comments(abs_path: str):
        with open(abs_path, 'r') as stream:
            yaml = YAML()
            data = yaml.load(stream=stream)
            stream.close()
            return data

    @staticmethod
    def write_yaml_with_comments(abs_path, data):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        try:
            with open(abs_path, 'w') as stream:
                # prevent sorting of keys
                yml = YAML()
                yml.indent(mapping=2, sequence=4, offset=2)
                serialized = yml.dump(data=data, stream=stream)
                stream.close()
                return serialized
        except NotADirectoryError as e:
            print(e)

    @staticmethod
    def read_yaml(abs_path):
        with open(abs_path, 'r') as stream:
            data = yaml.load(stream=stream, Loader=yaml.FullLoader)
            stream.close()
            return data

    @staticmethod
    def read_yamls_multi(paths: [str]):
        batch_size = min(len(paths), FileUtils.max_concurrent_files_limit())
        data = {}
        for chunk in batch(paths, batch_size):
            asyncio.run(_async_read_multi_yaml(chunk, data))

        for path in data:
            data[path] = yaml.load(stream=data[path], Loader=yaml.SafeLoader)
        return data

    @staticmethod
    def max_concurrent_files_limit():
        limit = os.getenv("ASSET_MAX_CONCURRENT_FILES")
        return int(limit) if limit else 1000

    @staticmethod
    def set_max_concurrent_files(num_files: int):
        """sets the maximum number of files that can be open at the same time, the default for osx is 256.
        This method gets called from AppSettings.post_init to apply the limit globally for all operations
        Parameters
        ----------
        num_files

        Returns
        -------

        """
        limit, max_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        if limit < num_files:
            try:
                resource.setrlimit(resource.RLIMIT_NOFILE, (num_files, -1))
            except ValueError as e:
                # linux will raise error if you are not superuser
                # we need to work with the limit set by os
                LoggingMixin.user_log.error(f"error:{e}. setting max concurrent files limit")
                os.environ["ASSET_MAX_CONCURRENT_FILES"] = str(limit - 20)  # keep some buffer

    @staticmethod
    def read_yaml_dir(dir):
        return FileUtils.read_yamls_multi(paths=list_files(root_dir=dir, pattern="*.yaml"))

    @staticmethod
    def write_yaml(abs_path, data):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        try:
            with open(abs_path, 'w') as stream:
                # prevent sorting of keys
                serialized = yaml.dump(data, stream,
                                       indent=4,
                                       sort_keys=False,
                                       default_flow_style=False,
                                       Dumper=NoAliasDumper)
                stream.close()
                return serialized
        except NotADirectoryError as e:
            print(e)

    @staticmethod
    def read_file(filepath: str, compressed: bool = False):
        if compressed:
            return FileUtils.read_zip_file(path=filepath)
        else:
            return FileUtils.read_text(abs_path=filepath)

    @staticmethod
    def write_file(abs_path: str, content: str, compressed: bool = False):
        if not os.path.exists(os.path.dirname(abs_path)):
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        try:
            if compressed:
                return FileUtils.write_zipfile(path=abs_path, content=content)
            else:
                return FileUtils._write_file_uncompressed(path=abs_path, content=content)
        except NotADirectoryError as e:
            print(e)

    @staticmethod
    def write_zipfile(path: str, content: str, key=None):
        if not path.endswith(".zip"):
            raise Exception("compressed file path must end with .zip")
        buffer = io.BytesIO()
        filename = key or os.path.basename(remove_suffix(path, ".zip"))
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(filename, str.encode(content, 'utf-8'))
        # https://stackoverflow.com/questions/18457678/python-write-in-memory-zip-to-file
        with open(path, "wb") as f:  # use `wb` mode
            f.write(buffer.getvalue())

    @staticmethod
    def _write_file_uncompressed(path: str, content: str):
        with open(path, 'w') as file:
            # prevent sorting of keys
            file.write(content)
            file.close()

    @staticmethod
    def read_text(abs_path, lines: bool = False):
        with open(abs_path, 'r') as fp:
            return fp.readlines() if lines else fp.read()

    @staticmethod
    def write_text(dst, content):
        with open(dst, 'w+') as fp:
            fp.write(content)

    @staticmethod
    def read_json(abs_path) -> dict:
        with open(abs_path, 'r') as stream:
            try:
                return json.load(stream) or {}
            except JSONDecodeError:
                return {}

    @staticmethod
    def write_json(data: dict, abs_path: str, sort_keys: bool = True):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as json_file:
            json_file.write(json.dumps(data or "", indent=4, sort_keys=sort_keys))

    @staticmethod
    def read_json_zip_dir(dir):
        zip_files = list_files(root_dir=dir, pattern="*.zip")
        data = []
        for file in zip_files:
            archived: dict = FileUtils.read_zip_file(path=file)
            for zipped in archived.values():
                data += json.loads(zipped)
        return data

    @staticmethod
    def read_zip_file(path: str) -> dict:
        result = {}
        with zipfile.ZipFile(path) as zf:
            for file in zf.namelist():
                with zf.open(file) as f:
                    result[file] = f.read()
        return result

    @staticmethod
    def read_zip_stream(zip_bytes: io.BytesIO):
        result = {}
        with zipfile.ZipFile(zip_bytes, "r") as zf:
            for file in zf.namelist():
                result[file] = zf.read(file)
        return result

    @staticmethod
    def file_hash(abs_path: str, hash_type="md5", b64=True) -> tuple:
        """"""
        if hash_type == "md5":
            return "md5", FileUtils.file_md5(abs_path, b64=b64)
        elif hash_type == "crc32c":
            return "crc32c", FileUtils.file_crc32c(abs_path, b64=b64)
        else:
            raise AssetException(msg=f"unsupported hash type: {hash_type}")

    @staticmethod
    def bytes_hash(file_bytes: bytes, hash_type="md5", b64=True) -> tuple:
        """"""
        if hash_type == "md5":
            return "md5", FileUtils.bytes_md5(file_bytes, b64=b64)
        elif hash_type == "crc32c":
            return "crc32c", FileUtils.bytes_crc32c(file_bytes, b64=b64)
        else:
            raise AssetException(msg=f"unsupported hash type: {hash_type}")

    @staticmethod
    def url_safe_md5(b64_md5: str):
        """converts base64 encoded md5 to urlsafe"""
        return base64.urlsafe_b64encode(base64.b64decode(b64_md5)).decode("ascii")

    @staticmethod
    def file_md5(f_name, b64=True):
        """calculates md5 hash and returns base64
        important: gcloud uses base64 encoded hashes
        """
        hash_md5 = hashlib.md5()
        try:
            with open(f_name, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            # return base64.b64encode(hash_md5.digest()).decode('ascii')
            if b64:
                return FileUtils.hex_to_base64(md5_hex=hash_md5.digest())
            # return the hex string
            return hash_md5.hexdigest()
        except IsADirectoryError as e:
            print(e)

    @staticmethod
    def file_crc32c(f_name, b64=True):
        hash_crc32c = crcmod.predefined.Crc('crc-32c')
        try:
            with open(f_name, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_crc32c.update(chunk)
            if b64:
                # return base64.b64encode(hash_crc32c.digest()).decode('ascii')
                return FileUtils.hex_to_base64(md5_hex=hash_crc32c.digest())
            # return the hex string
            return hash_crc32c.hexdigest()
        except IsADirectoryError as e:
            print(e)

    @staticmethod
    def bytes_md5(file_bytes, b64=True):
        hash_md5 = hashlib.md5()
        chunk_size = 4096
        start = 0
        while start < len(file_bytes):
            chunk = file_bytes[start:start + chunk_size]
            start += chunk_size
            hash_md5.update(chunk)
        if b64:
            # convert to base64
            return FileUtils.hex_to_base64(md5_hex=hash_md5.digest())
        # return the hex string
        return hash_md5.hexdigest()

    @staticmethod
    def bytes_crc32c(file_bytes, b64=True):
        hash_crc32c = crcmod.predefined.Crc('crc-32c')
        # hash_crc32c.update(file_bytes)
        chunk_size = 4096
        start = 0
        while start < len(file_bytes):
            chunk = file_bytes[start:start + chunk_size]
            start += chunk_size
            hash_crc32c.update(chunk)
        if b64:
            # convert to base64
            return FileUtils.hex_to_base64(md5_hex=hash_crc32c.digest())
        # return the hex string
        return hash_crc32c.hexdigest()

    @staticmethod
    def hex_to_base64(md5_hex: Union[bytes, str]):
        """base64 representation of the md5, we standardize it here to ensure
        that all asset-plugins follows the same protocol
        """
        if type(md5_hex) is str:
            md5_hex = md5_hex.encode("ascii")
        return base64.b64encode(md5_hex).decode('ascii')

    @staticmethod
    def string_md5(string: str, b64: bool = False):
        hash_md5 = hashlib.md5(string.encode('ascii'))
        if not b64:
            return hash_md5.hexdigest()
        else:
            return base64.b64encode(hash_md5.digest()).decode('ascii')

    @staticmethod
    def file_stat(file_path: str):
        return stat2dict(os.stat(file_path))

    @staticmethod
    def create_file_if_not_exists(path):
        """Create an empty file at path"""
        make_dirs(file_path=path)
        if not os.path.exists(path):
            with open(path, 'w') as fp:
                pass

    @staticmethod
    def delete_file(path):
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def create_large_file(path, gb: int):
        """creates file of certain size
        mainly for testing
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        size = 1024 * 1024 * 1024 * gb
        f = open(path, "wb")
        f.seek(size - 1)
        f.write(b"\0")
        f.close()

    @staticmethod
    def move(src, dst):
        """Move file and directories."""
        try:
            shutil.move(src, dst)
        except shutil.Error as e:
            raise AssetException(msg=f"error moving: {e}")

    @staticmethod
    def copy_file(src, dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src=src, dst=dst)

    @staticmethod
    def copy_dir(src: str, dst: str, ignore_list: list = None, exist_ok: bool = False):
        if ignore_list:
            shutil.copytree(src=src, dst=dst,
                            ignore=lambda dir, files: set(ignore_list),
                            dirs_exist_ok=exist_ok)
        else:
            shutil.copytree(src=src, dst=dst, dirs_exist_ok=exist_ok)

    @staticmethod
    def hard_link_file(src, dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.link(src, dst)

    @staticmethod
    def sym_link_file(src, dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.symlink(src, dst)

    @staticmethod
    def diff_file(from_file: str, to_file: str, from_desc: str, to_desc: str):
        with open(from_file) as src_file:
            src_text = src_file.readlines()

        with open(to_file) as dst_file:
            dst_text = dst_file.readlines()

        # Find and print the diff:
        diffs = ""
        for line in difflib.unified_diff(src_text,
                                         dst_text,
                                         fromfile=from_desc,
                                         tofile=to_desc,
                                         lineterm=''):
            diffs += f"{line}\n"
        return diffs

    @staticmethod
    def diff_file_html(from_file: str,
                       to_file: str,
                       diff_file: str,
                       html_template: str,
                       css_path: str,
                       desc: dict):
        from_file_lines = Path(from_file).read_text().splitlines()
        second_file_lines = Path(to_file).read_text().splitlines()
        html_diff = FileHtmlDiff(html_template=html_template, css_file=css_path)
        html_diff.set_description(title=desc.get("title"),
                                  subtitle=desc.get('subtitle'))
        Path(diff_file).write_text(
            html_diff.make_file(
                from_file_lines,
                second_file_lines,
                fromdesc=desc.get("from_desc"),
                todesc=desc.get("to_desc")
            ))

    @staticmethod
    def load_html_template(html_path: str, css_path: str = None, js_path: str = None):
        html = Path(html_path).read_text()
        if css_path:
            css = Path(css_path).read_text()
            html = html.replace("{{styles}}", f"\n{css}")
        if js_path:
            js = Path(css_path).read_text()
            html = html.replace("{{js}}", f"\n{js}")

        return html

    @staticmethod
    def clone_file(src, dst, force=False):
        if force:
            # remove file if exists
            if os.path.exists(dst):
                os.remove(dst)
            # write afresh
            FileUtils._os_file_clone(src, dst)
        else:
            # only create if not exists
            if not os.path.exists(dst):
                FileUtils._os_file_clone(src, dst)

    @staticmethod
    def hardlink_directories(src_dir: str, dst_dir: str):
        """recursively links all files from src to dst"""
        files = list_files(src_dir)
        for src_path in files:
            if os.path.exists(src_path) and os.path.isfile(src_path):
                dst_path = os.path.join(dst_dir, os.path.relpath(path=src_path, start=src_dir))
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)  # create subdirectory if not exists
                if not os.path.exists(dst_path):
                    os.link(src_path, dst_path)

    @classmethod
    def _os_file_clone(cls, src, dst):
        """clones a files, which creates a copy on write
        the new file has different inode and metadata but shares the same data blocks
        until they are edited by the user.
        - https://www.ctrl.blog/entry/file-cloning.html
        - https://developer.apple.com/documentation/foundation/file_system/about_apple_file_system?language=objc

        in APFS, cloning across volumes is not possible
        https://developer.apple.com/forums/thread/49188

        """
        # check if apfs or any other copy-on-write supported fs
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        fs_type = FileUtils.get_fs_type(dst)
        if fs_type.lower() == "apfs":
            FileUtils.clone_file_osx(src, dst)
        elif fs_type.lower() in FileUtils.linux_fs_cloning():
            FileUtils.clone_file_linux(src, dst)
        else:
            # cls.logger().warning(f"copy-on-write unsupported on file system: {fs_type}, using copy instead")
            FileUtils.clone_file_linux(src, dst)

    @staticmethod
    def linux_fs_cloning():
        """linux file systems that support file cloning
        source: https://www.ctrl.blog/entry/file-cloning.html
        """
        return {
            "bcachefs",
            "btrfs",
            "xfs",
            "ocfs2"
        }

    @staticmethod
    def clone_file_osx(src, dst):
        subprocess.run(["cp", "-c", src, dst])

    @staticmethod
    def clone_file_linux(src, dst):
        subprocess.run(["cp", "--", src, dst])

    @staticmethod
    def get_fs_type(path: str) -> str:
        """returns the file system type for a file"""
        root_type = ""
        for part in psutil.disk_partitions():
            if part.mountpoint == '/':
                root_type = part.fstype
                continue
            if path.startswith(part.mountpoint):
                return part.fstype
        return root_type

    @staticmethod
    def get_mount(path):
        path = os.path.realpath(os.path.abspath(path))
        while path != os.path.sep:
            if os.path.ismount(path):
                return path
            path = os.path.abspath(os.path.join(path, os.pardir))
        return path

    @staticmethod
    def print_file_tree(files: [str]):
        files = sorted(files)
        node = TreeNode.parse(paths=files)
        TreeNode.print_tree(node)

    # used in asset-server
    @staticmethod
    def write_binary(dst, content: bytes):
        with open(dst, 'wb') as f:
            # write the contents of the BytesIO object to the file
            f.write(content)

    # used in asset-server
    @staticmethod
    def write_json_to_stream(data: dict, stream: io.StringIO):
        json.dump(data, stream, indent=4, sort_keys=True)

    # used in asset-server
    @staticmethod
    def json_serialize(data):
        return json.dumps(data, indent=4, default=str)

    # used in asset-server
    @staticmethod
    def yaml_serialize(data):
        serialized = yaml.dump(
            data,
            indent=4,
            sort_keys=False,
            default_flow_style=False,
            Dumper=NoAliasDumper
        )
        return serialized

    # used in asset-server
    @staticmethod
    def write_yaml_to_stream(data: dict, stream: io.StringIO):
        yaml.dump(data,
                  stream,
                  indent=4,
                  sort_keys=False,
                  default_flow_style=False,
                  Dumper=NoAliasDumper)


async def _async_read_yaml(path, data):
    async with aiofiles.open(path, mode="r") as f:
        contents = await f.read()
        data[path] = contents


async def _async_read_multi_yaml(paths, data):
    await asyncio.gather(*[
        _async_read_yaml(path, data) for path in paths
    ])
