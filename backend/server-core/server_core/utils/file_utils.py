import yaml
import json
import hashlib
import base64
import os
from io import BytesIO
import zipfile


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


class FileUtils:
    @staticmethod
    def read_yaml(abs_path):
        with open(abs_path, 'r') as stream:
            data = yaml.load(stream=stream, Loader=yaml.FullLoader)
            stream.close()
            return data

    @staticmethod
    def write_yaml(abs_path, data):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as stream:
            # prevent sorting of keys
            serialized = yaml.dump(data,
                                   stream,
                                   indent=4,
                                   sort_keys=False,
                                   default_flow_style=False,
                                   Dumper=NoAliasDumper
                                   )
            stream.close()
            return serialized

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

    @staticmethod
    def read_text(abs_path) -> str:
        with open(abs_path, 'r') as fp:
            return fp.read()

    @staticmethod
    def write_text(dst, content):
        with open(dst, 'w+') as fp:
            fp.write(content)

    @staticmethod
    def write_binary(dst, content):
        with open(dst, 'wb') as f:
            # write the contents of the BytesIO object to the file
            f.write(content.get_bytes())

    @staticmethod
    def read_json(abs_path) -> dict:
        with open(abs_path, 'r') as stream:
            return json.load(stream)

    @staticmethod
    def write_json(data: dict, abs_path: str):
        if not data:
            return
        with open(abs_path, 'w') as json_file:
            json_file.write(json.dumps(data, indent=4, sort_keys=True))

    @staticmethod
    def file_hash(abs_path: str) -> tuple:
        """"""
        return "md5", FileUtils.file_md5(abs_path)

    @staticmethod
    def url_safe_md5(b64_md5: str):
        """converts base64 encoded md5 to urlsafe"""
        return base64.urlsafe_b64encode(base64.b64decode(b64_md5)).decode("ascii")

    @staticmethod
    def file_md5(f_name):
        """calculates md5 hash and returns base64
        important: gcloud uses base64 encoded hashes
        """
        hash_md5 = hashlib.md5()
        with open(f_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return base64.b64encode(hash_md5.digest()).decode('ascii')

    @staticmethod
    def string_md5(string: str, b64: bool = False):
        hash_md5 = hashlib.md5(string.encode('ascii'))
        if not b64:
            return hash_md5.hexdigest()
        else:
            return base64.b64encode(hash_md5.digest()).decode('ascii')

    @staticmethod
    def generate_zip(files: [tuple], dest: str):
        with zipfile.ZipFile(dest, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f[0], f[1])
            zf.close()

    @staticmethod
    def zip_in_memory(files: [tuple], path: str = None):
        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f[0], f[1])
        if path:
            with open(path, 'wb') as f:
                # write the contents of the BytesIO object to the file
                f.write(mem_zip.getvalue())
        return mem_zip.getvalue()

    @staticmethod
    def read_zip_file(path: str):
        result = {}
        with zipfile.ZipFile(path) as zf:
            for file in zf.namelist():
                with zf.open(file) as f:
                    result[file] = f.read()
        return result

    @staticmethod
    def json_serialize(data):
        return json.dumps(data, indent=4, default=str)


