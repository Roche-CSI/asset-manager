import logging

from asset_db.db import Database

logger = logging.getLogger(__name__)


class StoreDB(Database):
    """
    Stores Assets Meta information
    """
    type = "store-db"

    def add(self, **kwargs):
        """Adds to existing list of objects"""
        self.update(**kwargs)

    def get(self, key) -> dict:
        """Returns objects from yaml file"""
        return self.retrieve(key=key)

    def add_repo(self, repo_id, data: dict):
        # pop any existing repos that point to the same path
        # those are not valid anymore since 2 repos will never share the same path
        existing = self.data()
        repos = existing.get("repos") or {}
        ids = list(repos.keys())
        for id in ids:
            if repos[id].get('path') == data.get('path'):
                del repos[id]
        repos[repo_id] = data
        existing["repos"] = repos
        self._write_to_file(data=existing)

    def get_repos(self):
        return self.retrieve("repos") or {}

    def remove_repo(self, *repo_ids):
        if not repo_ids:
            return
        data = self.data()
        repos = data.get("repos")
        for repo_id in repo_ids:
            if repo_id in repos:
                del repos[repo_id]
        data["repos"] = repos
        self._write_to_file(data=data)

    def add_temp_asset(self, class_name, asset_data: dict) -> None:
        temp_assets = self.retrieve("temp_assets") or {}
        class_assets = temp_assets.get(class_name) or {}
        id = asset_data.get("seq_id")
        class_assets[id] = asset_data
        temp_assets[class_name] = class_assets
        self.update(temp_assets=temp_assets)

    def remove_temp_asset(self, class_name, seq_id):
        data = self.data()
        temp_assets = data.get("temp_assets") or {}
        class_assets = temp_assets.get(class_name, {})
        if seq_id in class_assets:
            del class_assets[seq_id]
        temp_assets[class_name] = class_assets
        data["temp_assets"] = temp_assets
        self._write_to_file(data=data)

    def list_temp_assets(self, class_name):
        temp_assets = self.retrieve("temp_assets") or {}
        return temp_assets.get(class_name, {})

    def remove(self, keys: list):
        """Deletes specific assets from the list

        Parameters
        ----------
        keys : list
            asset ids
        """
        data = self.data()
        for id in keys:
            deleted = data.pop(id, None)
            if deleted:
                pass
                # logger.info("asset {} removed.".format(id))
            else:
                logger.info("asset not added yet, ignoring remove for:{}".format(id))
        self._write_to_file(data)

    def clear(self):
        """Clears all assets"""
        self._write_to_file(data={})
