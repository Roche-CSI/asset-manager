import json
import os

from asset_core.asset.asset_version import ROOT_VERSION_NUMBER
from asset_core.asset.refs import AssetRef
from asset_core.configs import AppSettings, Configs
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils import comma_formatted, kilo_byte
from asset_utils.utils.cloud_utils import internet_on
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import colored_string, LogColors
from .repo import RepoAPI


class InfoAPI(RepoAPI):

    def list_refs(self, version=None, remote=False, jsonize=False):
        """Lists ot prints the inputs and dependents of the asset"""
        if remote:
            asset_version_name = f"{self.asset.name}/{version}" if version else self.asset.version.name
            return self.__class__.list_remote_refs(asset_name=asset_version_name,
                                                   project_id=self.asset.asset_class.project,
                                                   jsonize=jsonize)
        elif self.asset.refs:
            self.user_log.info(f"Listing the inputs of '{self.asset.name}/{ROOT_VERSION_NUMBER}':")
            local_refs = {
                "inputs": self.__class__.print_refs(refs=self.asset.refs,
                                                    exclude_columns=["dst"],
                                                    jsonize=jsonize)
            }
            if jsonize:
                return local_refs
            self.user_log.message(f"upload the asset to commit pending inputs {UserCommands().upload_asset()}")
        else:
            self.user_log.info(f"no inputs found locally for: {self.asset.version.name}")
            self.user_log.message(UserCommands().inputs_info_remote())
            self.user_log.message(UserCommands().switch_asset_version())

    def print_object_url(self, rel_file_path: str, jsonize=False):
        """Prints the url of the object given the file path.

        The file path should be relative to the asset root.
        """
        objects = self.asset.objects.filter(predicate=lambda x: x.path == rel_file_path)
        if not objects:
            raise exceptions.AssetException(msg=f"file not found: {rel_file_path}")

        asset_obj = objects[0]
        if not asset_obj.is_committed:
            e = exceptions.AssetException(msg=f"file not uploaded yet: {rel_file_path}")
            e.logs.add("you must upload a file to get the url")
            raise e

        object_url = os.path.join(Configs.shared().asset_home.dashboard_url,
                                  "asset", self.project_id, self.asset.name,
                                  f"files?version={self.asset.version.number}&object={asset_obj.id}")
        if jsonize:
            return object_url

        print(object_url)

    @classmethod
    def list_remote_refs(cls, asset_name: str, project_id: str, jsonize=False):
        """Lists the inputs and dependents of the asset from the server"""
        try:
            refs, sanitized_name = AssetRef.get_refs_from_remote(asset_name=asset_name, project_id=project_id)
            if refs.get("error"):
                # server sends back error, if asset is not found
                raise exceptions.AssetNotFoundError(refs.get("error"))
            if jsonize:
                return {
                    "inputs": cls.print_refs(refs.get("depends_on"), jsonize=jsonize),
                    "dependents": cls.print_refs(refs.get("dependents"), jsonize=jsonize)
                }
            cls.user_log.info(f"Listing the inputs of '{sanitized_name}':")
            if refs.get("depends_on"):
                cls.print_refs(refs.get("depends_on"), exclude_columns=["dst"])
            else:
                cls.user_log.message("None")
            cls.user_log.info(f"Listing the assets that take '{sanitized_name}' as input:")
            if refs.get("dependents"):
                cls.print_refs(refs.get("dependents"), exclude_columns=["src"])
            else:
                cls.user_log.message("None")
            return refs, sanitized_name
        except exceptions.ServerNotAvailableError as e:
            # connection error, we need to check if internet or server
            if not internet_on():
                message = "Unable to connect, make sure you are connected to internet"
            else:
                message = "Asset Server not available. You need to be connected to Roche VPN to access the server"
            e.logs.add(message)
            raise
        except exceptions.AssetException:
            raise

    @classmethod
    def print_refs(cls, refs, exclude_columns=[], jsonize=False):
        data = [
            {
                "ref_id": ref.id or "None",
                "src": ref.src_version.get("name"),
                "dst": ref.dst_version.get("name"),
                "label": ref.label,
                "created_by": ref.created_by,
                "created_at": ref.created_at,
                "status": ref.get_state()
            } for ref in refs
        ]
        if jsonize:
            return data
        columns = {
            "ref_id": "ID",
            "src": "Input",
            "dst": "Asset",
            "label": "Label",
            "created_by": "Created By",
            "created_at": "Created At",
            "status": "Status"
        }
        for column in exclude_columns:
            columns.pop(column, None)
        cls.user_log.table(columns=columns, rows=data, table_fmt="plain")

    def list_alias(self):
        print(self.asset.alias)

    def print_name(self):
        # using print here because this may be used for piping
        # user logs adds extra chars for color formatting
        print(self.asset.version.name)

    def print_alias_name(self):
        if not self.asset.alias:
            raise exceptions.AssetException(msg="no alias assigned to the asset")
        print(f"{self.asset.asset_class.name}/{self.asset.alias}/{self.asset.version.number}")

    def print_hash(self):
        print(self.asset.objects.hash)

    def print_metadata(self):
        if not self.asset.metadata:
            raise exceptions.AssetException(msg="no metadata found for the asset")
        print(json.dumps(self.asset.metadata, indent=4))

    def print_attributes(self):
        if not self.asset.attributes:
            raise exceptions.AssetException(msg="no attributes found for the asset")
        print(json.dumps(self.asset.attributes, indent=4))

    def asset_info(self, large=False, jsonize=False):
        if not self.asset.repo.current_asset:
            e = exceptions.AssetNotFoundError(msg="no active asset found")
            e.logs.add(UserCommands().clone_asset())
            e.logs.add(UserCommands().create_asset())
            e.logs.add(UserCommands().list_assets())
            raise e

        return {
            "asset": self.print_asset(jsonize=jsonize),
            "objects": self.print_objects(large=large, jsonize=jsonize)
        }

    def asset_tree(self):
        if not self.asset.repo.current_asset:
            e = exceptions.AssetNotFoundError(msg="no active asset found")
            e.logs.add(UserCommands().clone_asset())
            e.logs.add(UserCommands().create_asset())
            e.logs.add(UserCommands().list_assets())
            raise e

        paths = [obj.path for obj in self.asset.objects]
        FileUtils.print_file_tree(files=paths)

    def print_asset(self, jsonize=False):
        """Prints the asset and file information"""
        project: dict = AppSettings.shared().projects.get(self.asset.asset_class.project)
        if not project:
            raise exceptions.InvalidProjectError()

        columns = {
            "section": "",
            "details": "",
        }
        rows = self.asset_summary(asset=self.asset, project=project, jsonize=jsonize)
        if jsonize:
            return rows

        files_heading = "cloning"
        file_section = ""

        if rows["cloning"][0]:
            # asset was cloned
            if rows["cloning"][1] == "empty_asset":
                files_heading = colored_string(files_heading, LogColors.INFO)
                file_section = colored_string("there are no files in the asset\n", LogColors.INFO)
                file_section += f"{UserCommands().add_to_asset()}"
            else:
                files_heading = colored_string(files_heading, LogColors.ACTIVE)
                file_section += "all files were linked - asset fully cloned\n"
                file_section = colored_string(file_section, color=LogColors.ACTIVE)
        else:
            if rows["cloning"][1] == "temp_asset":
                # not cloneable yet
                files_heading = colored_string(files_heading, LogColors.INFO)
                file_section = colored_string("local asset, upload to make it available for cloning\n",
                                              color=LogColors.INFO)
                file_section += f"{UserCommands().upload_asset()}"
            else:
                files_heading = colored_string(files_heading, LogColors.ALERT)
                file_section += colored_string("files not available locally\n", color=LogColors.ALERT)
                file_section += f"{UserCommands().download_asset()}"

        # check linking type
        if rows["linking_type"] != "copy":
            self.user_log.alert(
                f"Read-only asset, no changes can be made: asset was cloned with {rows['linking_type']}")

        # remove cloning key
        rows.pop("cloning", None)

        rows[f"{files_heading}"] = file_section
        rows["remote"] = rows["remote"] or "not assigned yet"

        data = [{"section": f"{key}: ", "details": rows[key]} for key in rows]
        self.user_log.table(columns=columns, rows=data, table_fmt="plain")

    def asset_summary(self, asset, project, jsonize=False) -> dict:
        """Returns a summary info of the asset."""
        summary = {
            "project": project.get("name"),
            "asset": asset.name,
            "title": asset.title,
            "version": asset.version.number,
            "size": asset.objects.size,
            "hash": asset.objects.hash,
            "created_by": asset.created_by,
            "created_at": asset.created_at,
            "asset id": asset.id,
            "asset class": asset.asset_class.name,
            "alias": self.asset.alias,
            "tags": asset.tags,
            "metadata": asset.metadata,
            "attributes": asset.attributes,
            "inputs": [str(ref) for ref in self.asset.refs],
            "remote": self.asset.remote_url,
            "linking_type": self.asset.repo.linking_type,
            "description": asset.description,
        }
        # add summary["cloning"] key
        if asset.is_temp:
            summary["cloning"] = (False, "temp_asset")
        elif len(asset.objects) == 0:
            # this is a possibility - user might remove all files in the next version
            summary["cloning"] = (True, "empty_asset")
        elif asset.objects.linked():
            summary["cloning"] = (True, "success")
        else:
            summary["cloning"] = (False, "not_cloned")
        if jsonize:
            return summary

        # convert to string for printing
        summary["size"] = f"{comma_formatted(kilo_byte(summary['size']))} KB"
        summary["tags"] = ", ".join(asset.tags) if asset.tags else "None"
        if not summary["title"]:
            summary["title"] = "None"
        if not summary["version"]:
            summary["version"] = "None"
        if not summary["alias"]:
            summary["alias"] = "None"
        if not summary["description"]:
            summary["description"] = "None"
        if summary["metadata"]:
            summary["metadata"] = f"Available {UserCommands().asset_info_metadata()}"
        else:
            summary["metadata"] = "None"
        if summary["attributes"]:
            summary["attributes"] = f"Available {UserCommands().asset_info_attributes()}"
        else:
            summary["attributes"] = "None"
        return summary

    def print_objects(self,
                      objects=None,
                      base_dir=os.getcwd(),
                      large=False,
                      jsonize=False):
        """Prints the information of the objects in the asset"""
        objects = objects or self.asset.objects
        if not objects:
            return
        data = self.print_objects_table(objects, base_dir, large, jsonize)
        if jsonize:
            return data
        self.user_log.message(UserCommands().asset_status())

    def list_current_version(self):
        result = ""
        for field in self.asset.version.__class__.serialize_fields():
            result += f"{field}: {getattr(self.asset.version, field)} \n"
        self.user_log.message(body=result, title=f"asset: {self.asset.name}")

    def print_objects_table(self, objects,
                            base_dir=os.getcwd(),
                            large=False,
                            jsonize=False):
        objects_data = [self.object_summary(obj=obj, large=large) for obj in objects]
        if jsonize:
            return objects_data

        if large:
            columns = {
                "index": "#",
                "path": "Location",
                "content_type": "Content-Type",
                "file_id": "File Id",
                "size": "Size",
                "cloned": "Cloned",
                "hash": "Hash",
                "storage_id": "Storage",
                "created_by": "Added-By",
                "created_at": "Added-At",
            }
            col_align = ["left", "left", "right", "right", "right", "right", "right", "right", "right", "right"]
        else:
            columns = {
                "index": "#",
                "path": "Location",
                "size": "Size",
                "cloned": "Cloned",
            }
            col_align = ["left", "left", "right", "right"]

        # sort the objects by path for before printing the table
        objects_data = sorted(objects_data, key=lambda x: x['path'])

        has_proxy = False
        # modify the data rows for better readability
        for idx, row in enumerate(objects_data):
            row["index"] = str(idx)
            row["path"] = f"{os.path.relpath(row['linked_path'], base_dir)}" \
                          f"{colored_string(' *', LogColors.off_white) if row.get('proxy') else ''}"
            del row["linked_path"]  # pop it, we don't need anymore
            row["size"] = f"{comma_formatted(kilo_byte(row['size']))} KB"
            row["cloned"] = colored_string("\u2713", LogColors.ACTIVE) \
                if row["cloned"] else colored_string("\u2715", LogColors.red)
            has_proxy = has_proxy or row.get("proxy")

        if has_proxy:
            legends = f"{colored_string('proxy objects: [*]', LogColors.cyan)}\n"
            self.user_log.message(legends)

        self.user_log.table(columns=columns,
                            rows=objects_data,
                            table_fmt="simple",
                            col_align=col_align,
                            paged=False)

    def object_summary(self, obj, large=False):
        """Returns info of each object in the asset"""
        if large:
            return {
                "linked_path": obj.linked_path,
                "path": obj.path,
                "size": obj.content.size,
                "hash": (obj.content.hash_type, obj.content.hash_value),
                "storage_id": obj.content.storage_id,
                "content_type": obj.content.mime_type,
                "created_by": obj.created_by,
                "created_at": obj.created_at,
                "proxy": obj.content.is_proxy,
                "url": obj.content.source_url if obj.content.is_proxy else obj.content.remote_url,
                "file_id": obj.content.file_id,
                "cloned": obj.linked()
            }
        else:
            return {
                "linked_path": obj.linked_path,
                "path": obj.path,
                "size": obj.content.size,
                "cloned": obj.linked(),
            }
