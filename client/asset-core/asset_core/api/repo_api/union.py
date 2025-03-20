from __future__ import annotations

import base64
import json
import os
import tempfile

from asset_core.api.repo_api.diff import DiffSymbols, DiffApi
from asset_core.api.repo_api.repo import RepoAPI
from asset_core.objects.asset_object import AssetObject
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils import web_utils
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LogColors, colored_string


class UnionApi(RepoAPI):

    def union(self, target_version: str, file: str, continue_file: str):
        """combines the target version with current version of the asset

        Parameters
        ----------
        target_version: str
        meta_file: file

        Returns
        -------

        """
        if continue_file:
            self.continue_union(file=continue_file)
        else:
            self.generate_dryrun_file(target_version, file)

    def continue_union(self, file):
        # read from meta-file and combine
        comments, contents = self.parse_combine_dryrun_file(filepath=file)
        if not comments or not contents:
            self.user_log.error(f"error in parsing file:{file}")
            return

        # verify asset-id
        union_hash = self.extract_union_hash(comments=comments)
        try:
            src_ver, dst_ver = self.validate_union_hash(hash_string=union_hash)
            diffs = self.__class__.parse_combine_data(contents=contents)
            self.validate(diffs=diffs, src_ver=src_ver, dst_ver=self.asset.version.number)
            self.apply_union_patch(diffs=diffs, src_ver=src_ver, dst_ver=dst_ver)
        except exceptions.AssetException:
            raise

    def validate_union_hash(self, hash_string: str):
        hashed_data: dict = self.__class__.parse_union_hash(hash_string=hash_string)
        if hashed_data.get("asset_id") != self.asset.id:
            raise exceptions.AssetException(msg="invalid data, unable continue combine operation")

        # verify target_version is the current version
        if hashed_data.get("src_ver") != self.asset.version.number:
            msg = f"invalid target, you must switch to: {hashed_data.get('dst_ver')} to be able to continue operations"
            raise exceptions.AssetException(msg=msg)

        # make sure source version is present
        if not hashed_data.get("dst_ver"):
            raise exceptions.AssetException(
                msg="missing target version to perform union operations, please run: 'asset union <target_version>'")

        # make sure, it's a valid version
        versions = self.asset.cached_versions()
        for version in versions:
            if hashed_data.get("dst_ver") == version.get("number"):
                return hashed_data.get("src_ver"), hashed_data.get("dst_ver")

        msg = f"invalid version:{hashed_data.get('src_ver')} for asset:{self.asset.name}"
        raise exceptions.AssetException(msg=msg)

    def apply_union_patch(self, diffs: dict, src_ver: str, dst_ver: str):
        # keep it separately in a list, since we are going to modify the asset.objects here
        src_objects: [AssetObject] = self.asset.list_objects()
        dst_objects: [AssetObject] = self.asset.list_objects(ver_number=dst_ver)

        # apply patches
        add_local, add_remote = self.patch_add(diffs=diffs, dst_objects=dst_objects)
        removed = self.patch_removed(diffs=diffs, src_objects=src_objects)
        alter_local, alter_remote = self.patch_altered(diffs=diffs,
                                                       src_objects=src_objects,
                                                       dst_version=dst_ver,
                                                       dst_objects=dst_objects)

        if add_local or add_remote or removed or alter_local or alter_remote:
            self.user_log.success(f"success: completed union of {dst_ver} with {src_ver}")
            self._print_format(msg="added new files", local=add_local, remote=add_remote, color=LogColors.green)
            self._print_format(msg="removed unwanted files", local=removed, remote=[], color=LogColors.red)
            self._print_format(msg="altered files", local=alter_local, remote=alter_remote, color=LogColors.yellow)
            self.user_log.message(UserCommands().asset_status())
            self.user_log.message(UserCommands().upload_asset())
        else:
            self.user_log.info(f"no changes required for union of {dst_ver} with {src_ver}")

    def _print_format(self, msg: str,
                      local: [AssetObject],
                      remote: [AssetObject],
                      color=None
                      ):
        if not local and not remote:
            return ""

        msg = f"{msg}:\n"
        msg += self.user_log.bulletize(items=[obj.path for obj in local + remote])
        if remote:
            msg += "following files are not available locally, run asset-download to fetch them\n"
            msg += self.user_log.bulletize(items=[obj.path for obj in remote])
            msg += UserCommands().download_asset()

        self.user_log.message(body=msg, color=color)

    def patch_add(self, diffs: dict, dst_objects: [AssetObject]) -> tuple:
        # get objects from src_version
        added = diffs.get("added", {})
        if not added.get("files", []):
            return [], []

        files_to_add = set()
        for file_obj in added.get("files", []):
            file, option = file_obj["file"], file_obj["option"]
            if option and str(option).lower() == "y":
                files_to_add.add(file)

        return self._add_and_link_objects(objects=[obj for obj in dst_objects if obj.path in files_to_add])

    def patch_removed(self, diffs: dict, src_objects: [AssetObject]) -> list:
        """remove any unwanted files from the union
        Parameters
        ----------
        diffs
        src_objects

        Returns
        -------
        list:
            removed objects

        """
        # add back missing
        remove = diffs.get("removed", {})
        if not remove.get("files", []):
            return []

        files_to_remove = set()
        for file_obj in remove.get("files", []):
            file, option = file_obj["file"], file_obj["option"]
            if option and str(option).lower() == "y":
                files_to_remove.add(file)

        return self._remove_and_unlink_objects(objects=[obj for obj in src_objects if obj.path in files_to_remove])

    def patch_altered(self, diffs: dict,
                      dst_version: str,
                      src_objects: [AssetObject],
                      dst_objects: [AssetObject]):
        # alter files
        altered = diffs.get("altered", {})
        # change files from src or dst version
        if not altered.get("files", []):
            return [], []

        files_to_alter = set()
        for file_obj in altered.get("files", []):
            file, option = file_obj["file"], file_obj["option"]
            if option and str(option).lower() == dst_version:
                files_to_alter.add(file)

        objects_to_remove = [obj for obj in src_objects if obj.path in files_to_alter]
        objects_to_add = [obj for obj in dst_objects if obj.path in files_to_alter]

        return self._alter_and_relink_objects(add_objects=objects_to_add, remove_objects=objects_to_remove)

    def _add_and_link_objects(self, objects: [AssetObject]):
        if not objects:
            return [], []

        existing_ids = [obj.id for obj in self.asset.objects]
        objects_to_add = [obj for obj in objects if obj.id not in existing_ids]
        if not objects_to_add:
            return [], []

        self.asset.set_state(self.asset.states.PENDING, save=True)
        # restore from cache
        remote_objects = []  # not all objects may be available locally
        for obj in objects_to_add:
            # add back files from cache
            _ = obj.link_from_store()
        self.asset.add_objects(objects=objects_to_add)
        return objects_to_add, remote_objects

    def _remove_and_unlink_objects(self, objects: [AssetObject]):
        if not objects:
            return []
        self.asset.set_state(self.asset.states.PENDING, save=True)
        self.asset.remove_objects(targets=objects, delete=True)
        return objects

    def _alter_and_relink_objects(self, add_objects: [AssetObject], remove_objects: [AssetObject]):
        if not add_objects and not remove_objects:
            return [], []
        # remove common, no point in removing and then adding back - user might rerun union operations
        add_ids = set([obj.id for obj in add_objects])
        self._remove_and_unlink_objects(objects=[obj for obj in remove_objects if obj.id not in add_ids])
        return self._add_and_link_objects(objects=add_objects)

    def validate(self, diffs: dict, src_ver: str, dst_ver: str):
        # add files
        added: dict = diffs.get("added")
        if added.get("all"):
            if added.get("all").lower() not in ["y", "n"]:
                msg = "invalid option specified for 'Select All' in ADDED, please choose either 'Y' or 'N'"
                self.user_log.error(message=msg)
                return False
                # apply all to every file
            for file in added.get("files", []):
                file["option"] = added.get("all")

        # remove files
        remove: dict = diffs.get("removed")
        if remove.get("all"):
            if remove.get("all").lower() not in ["y", "n"]:
                msg = "invalid option specified for 'Select All' in REMOVED, please choose either 'Y' or 'N'"
                self.user_log.error(message=msg)
                return False
                # apply all to every file
            for file in remove.get("files", []):
                file["option"] = remove.get("all")

        # altered files
        altered: dict = diffs.get("altered")
        if altered.get("all"):
            if altered.get("all").lower() not in [src_ver, dst_ver]:
                msg = f"invalid option specified for 'Select All' in ALTERED, please choose either {src_ver} or {dst_ver}"
                self.user_log.error(message=msg)
                return False
                # apply all to every file
            for file in altered.get("files", []):
                file["option"] = altered.get("all")

        return True

    @classmethod
    def parse_combine_dryrun_file(cls, filepath: str) -> tuple:
        lines: [str] = FileUtils.read_text(filepath, lines=True)
        # remove comments
        comments, data = [], []
        for line in lines:
            line = line.strip("\n")
            if not line:
                continue
            if line.startswith(DiffSymbols.COMMENT.value):
                comments.append(line.strip(DiffSymbols.COMMENT.value))
            else:
                data.append(line)
        return comments, data

    @classmethod
    def extract_union_hash(cls, comments: str):
        # parse id
        combine_id = None
        for line in comments:
            if "union_hash" in line:
                comps: [str] = line.split(":")
                combine_id = comps[1].strip()
        return combine_id

    @classmethod
    def parse_combine_data(cls, contents: [str]):
        diffs = {
            "added": {"all": None, "files": []},
            "removed": {"all": None, "files": []},
            "altered": {"all": None, "files": []}
        }
        for line in contents:
            cols: [str] = line.split("|")
            # remove empty strings
            cols = [string.strip() for string in cols if string]
            if len(cols) < 4:
                continue
            symbol: str = cols[0]
            option: str = cols[3]
            if symbol == DiffSymbols.ALL_ADDED.value:
                diffs["added"]["all"] = option or None
            elif symbol == DiffSymbols.ALL_REMOVED.value:
                diffs["removed"]["all"] = option or None
            elif symbol == DiffSymbols.ALL_ALTERED.value:
                diffs["altered"]["all"] = option or None
            elif symbol == DiffSymbols.ADDED.value:
                diffs["added"]["files"].append({
                    "file": cols[1],
                    "option": option or None
                })
            elif symbol == DiffSymbols.REMOVED.value:
                diffs["removed"]["files"].append({
                    "file": cols[1],
                    "option": option or None
                })
            elif symbol == DiffSymbols.ALTERED.value:
                diffs["altered"]["files"].append({
                    "file": cols[1],
                    "option": option or None
                })
            else:
                continue
        return diffs

    @classmethod
    def get_union_hash(cls, asset_id: str, src_ver: str, dst_ver: str):
        data = {"asset_id": asset_id, "src_ver": src_ver, "dst_ver": dst_ver}
        return base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")

    @classmethod
    def parse_union_hash(cls, hash_string: str):
        return json.loads(base64.b64decode(hash_string.encode("utf-8")).decode("utf-8"))

    def generate_dryrun_file(self, target_ver: str, file: str):
        try:
            src_ver = self.asset.version.number
            dst_ver = target_ver
            diff_api = DiffApi(asset=self.asset)
            added, removed, altered = diff_api.generate_version_diff(src_ver=src_ver, dst_ver=target_ver)
            # merge into a uniform dict to create html table

            union_hash = self.get_union_hash(asset_id=self.asset.id, src_ver=src_ver, dst_ver=dst_ver)
            temp_dir = tempfile.mkdtemp()
            tf = os.path.join(temp_dir, f"{union_hash[:8]}.txt")

            cmt = DiffSymbols.COMMENT.value
            cmt_block = 3 * cmt
            comments = f"{cmt_block} DRY RUN: version {src_ver} union with {target_ver} for asset: {self.asset.name}\n"
            comments += f"{cmt} union_hash: {union_hash}\n"
            comments += f"{cmt} summary changes to be committed for creating a union of version {dst_ver} and {src_ver}\n"
            comments += f"{cmt} this file is generated at: {tf}\n"
            comments += f"{cmt} open this file in a text editor and update the changes you want to customize\n"
            comments += f"{cmt} use: 'asset union --continue {tf}' to complete the union process\n"
            comments += f"{cmt_block}\n\n"

            text = comments
            if added:
                choices = "[Y / N]"
                text += f"{cmt_block} EXTRA FILES: {dst_ver} has additional files w.r.t {src_ver} \n"
                text += f"{cmt} these files will be added because of union operations\n"
                text += f"{cmt} change to 'N' if you want to exclude any of these file\n"
                text += f"{cmt} use 'Select All' to apply the instructions to all files\n"
                text += f"{cmt_block} choose from: {choices}\n"
                data = []
                # select all choice
                if len(added) > 1:
                    data.append({
                        "change_type": DiffSymbols.ALL_ADDED.value,
                        "file": "Select All",
                        "choices": choices,
                        "selected": ""
                    })
                    # blank line
                    data.append({
                        "change_type": "-" * 10,
                        "file": "-" * 30,
                        "choices": "",
                        "selected": ""
                    })
                for file in added:
                    data.append({
                        "change_type": DiffSymbols.ADDED.value,
                        "file": file,
                        "choices": choices,
                        "selected": "Y"
                    })

                cols = {"change_type": DiffSymbols.ADDED.name, "file": "File", "choices": "Choices",
                        "selected": f"Add Files from {dst_ver}"}
                text += self.user_log.table_formatted(columns=cols, rows=data)
                text += "\n\n"

            if removed:
                choices = "[Y / N]"
                text += f"{cmt_block} MISSING FILES: files missing in {dst_ver} w.r.t {src_ver}\n"
                text += f"{cmt} these files will be re-added because of union operations\n"
                text += f"{cmt} change to 'Y', if you don't want to add any of these files\n"
                text += f"{cmt} use 'Select All' to apply the instructions to all files\n"
                text += f"{cmt_block} choose from: {choices}\n"
                data = []
                # select all choice
                if len(removed) > 1:
                    data.append({
                        "change_type": DiffSymbols.ALL_REMOVED.value,
                        "file": "Select All",
                        "choices": choices,
                        "selected": ""
                    })
                    # blank line
                    data.append({
                        "change_type": "-" * 10,
                        "file": "-" * 30,
                        "choices": "",
                        "selected": ""
                    })
                for file in removed:
                    data.append({
                        "change_type": DiffSymbols.REMOVED.value,
                        "file": file,
                        "choices": choices,
                        "selected": "N"
                    })

                cols = {"change_type": DiffSymbols.REMOVED.name, "file": "File", "choices": "Choices",
                        "selected": f"Remove Files from {src_ver}"}
                text += self.user_log.table_formatted(columns=cols, rows=data)
                text += "\n\n"

            if altered:
                choices = f"[{src_ver} / {dst_ver}]"
                text += f"{cmt_block} ALTERED FILES: files altered in {dst_ver} w.r.t {src_ver}\n"
                text += f"{cmt} the changes will be retained because of combine\n"
                text += f"{cmt} change to '{src_ver}', if you want to undo any changes to the file\n"
                text += f"{cmt} use 'Select All' to apply the instructions to all files\n"
                text += f"{cmt_block} choose from: {choices}\n"

                data = []
                # select all choice
                if len(altered) > 1:
                    data.append({
                        "change_type": DiffSymbols.ALL_ALTERED.value,
                        "file": "Select All",
                        "choices": choices,
                        "selected": ""
                    })
                    # blank line
                    data.append({
                        "change_type": "-" * 10,
                        "file": "-" * 30,
                        "choices": "",
                        "selected": ""
                    })
                for file in altered:
                    data.append({
                        "change_type": DiffSymbols.ALTERED.value,
                        "file": file,
                        "choices": choices,
                        "selected": dst_ver
                    })

                cols = {"change_type": DiffSymbols.ALTERED.name, "file": "File", "choices": "Choices",
                        "selected": "Use File from Version"}
                text += self.user_log.table_formatted(columns=cols, rows=data)

            FileUtils.write_text(dst=tf, content=text)
            # FileUtils.write_yaml(tf, yaml_data)
            msg = colored_string(f"review the dry-run file named: {os.path.basename(tf)} at: {os.path.dirname(tf)}\n",
                                 LogColors.INFO)
            self.user_log.message(f"file:{tf}")
            msg += UserCommands().union_continue()
            self.user_log.message(msg)
            web_utils.open_in_browser(tf)

        except exceptions.AssetException as e:
            self.user_log.message(e.msg, color=LogColors.ERROR)
