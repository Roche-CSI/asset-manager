import copy
import os

from asset_core.asset.asset_class import AssetClass
from asset_core.store import Repo
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors
from .store import StoreAPI


class ListAPI(StoreAPI):

    def list_classes(self, jsonize=False):
        self.user_log.message("Listing asset-classes")
        data = AssetClass.list_classes(store=self.store)
        if jsonize:
            return data
        self.print_asset_classes_table(data)
        cmd = UserCommands()
        self.user_log.message("\n".join([cmd.list_assets(), cmd.fetch_classes(), cmd.list_help()]))

    def list_assets(self, class_name, include_locations=False):
        if not class_name:
            message = "there is not active asset-class, to view the list of assets in a class: "
            message += UserCommands().list_assets()
            message += "\nto view the list of classes: "
            message += UserCommands().list_classes()
            self.user_log.message(message)
            return

        asset_class = AssetClass.get_asset_class(store=self.store, name=class_name)
        assets = asset_class.list_assets()
        if not assets:
            message = f"no assets found for class {class_name}\n"
            message += UserCommands().fetch_assets()
            self.user_log.message(message)
            return
        self.user_log.message(f"Listing assets for class: {class_name}")
        if include_locations:
            assets_list_data = self._update_locations(assets=assets)
        else:
            assets_list_data = sorted(assets.values(), key=lambda x: self.parse_seq_id(x.get("seq_id")))
        # print assets list table
        self.print_assets_list_table(class_name=class_name,
                                     assets=assets_list_data,
                                     include_locations=include_locations)
        cmd = UserCommands()
        self.user_log.message("\n".join([cmd.clone_asset(), cmd.fetch_assets(), cmd.list_help()]))

    def _update_locations(self, assets):
        repos: dict = self.store.list_repos()
        locations = {}
        for repo_id, repo_data in repos.items():
            existing = locations.get(repo_data.get("asset")) or []
            repo_path = repo_data.get("path")
            # check if it's a valid repo, user may have deleted or moved
            if Repo.is_valid(path=repo_path, id=repo_id):
                existing.append(os.path.relpath(start=os.getcwd(), path=repo_data.get("path")))
                # existing.append(repo_data.get("path"))
            else:
                existing.append("not cloned")
            locations[repo_data.get("asset")] = existing

        with_location = []
        asset_data = sorted(assets.values(), key=lambda x: self.parse_seq_id(x.get("seq_id")))
        for asset in asset_data:
            repos = locations.get(asset.get("id"))
            if repos:
                for repo in repos:
                    # make copy
                    data = copy.deepcopy(asset)
                    data["location"] = repo
                    with_location.append(data)
            else:
                with_location.append(asset)
        return with_location

    def print_assets_list_table(self, class_name: str, assets: list, include_locations=False):
        columns = {
            "index": "#",
            "name": "Asset Name",
            "id": "ID",
            "owner": "Owner",
            "alias": "Alias",
            "created_by": "Created-By",
            "created_at": "Created-At",
        }
        if include_locations:
            columns["location"] = "Location"
        data = [{
            "index": self.active_asset_color(obj.get("id"), location=obj.get("location"), string=str(idx + 1)),
            "name": self.active_asset_color(obj.get("id"), location=obj.get("location"),
                                            string=os.path.join(class_name, str(obj.get("seq_id")))),
            "id": self.active_asset_color(obj.get("id"), location=obj.get("location"), string=obj.get("id")),
            "owner": self.active_asset_color(obj.get("id"), location=obj.get("location"), string=obj.get("owner")),
            "alias": self.active_asset_color(obj.get("id"), location=obj.get("location"), string=obj.get("alias")),
            "location": self.active_asset_color(obj.get("id"), location=obj.get("location"),
                                                string=obj.get("location")),
            "created_by": self.active_asset_color(obj.get("id"), location=obj.get("location"),
                                                  string=obj.get("created_by")),
            "created_at": self.active_asset_color(obj.get("id"), location=obj.get("location"),
                                                  string=obj.get("created_at")),
        }
            for idx, obj in enumerate(assets)
        ]
        self.user_log.table(columns=columns, rows=data)

    def parse_seq_id(self, seq_id):
        if not seq_id:
            raise exceptions.AssetException("seq_id can not be null")
        if type(seq_id) is int:
            return seq_id
        parsed = int(seq_id[len("temp_"):])
        return parsed

    def active_asset_color(self, id, location, string):
        if not location:
            return string
        if self.repo and \
                self.repo.current_asset.get("id") == id and \
                location == os.curdir:
            return colored_string(string, color=LogColors.ACTIVE)
        return string

    def print_asset_classes_table(self, classes):
        if not classes:
            message = colored_string("there are no asset-classes available locally \n", LogColors.INFO)
            # message += f"{UserCommands().fetch_classes()}"
            self.user_log.message(message)
            return

        columns = {
            "index": "#",
            "name": "Name",
            "id": "ID",
            "created_by": "Created-By",
            "created_at": "Created-At",
        }
        data = [{
            "index": self.active_class_color(name=obj.get("name"), string=str(idx + 1)),
            "name": self.active_class_color(name=obj.get("name"), string=obj.get("name")),
            "id": self.active_class_color(name=obj.get("name"), string=obj.get("id")),
            "created_by": self.active_class_color(name=obj.get("name"), string=obj.get("created_by")),
            "created_at": self.active_class_color(name=obj.get("name"), string=obj.get("created_at")),
        }
            for idx, obj in enumerate(classes.values())
        ]
        self.user_log.table(columns=columns, rows=data)

    def active_class_color(self, name, string):
        if self.repo and self.repo.current_asset.get("class_name") == name:
            return colored_string(string, color=LogColors.ACTIVE)
        return string
