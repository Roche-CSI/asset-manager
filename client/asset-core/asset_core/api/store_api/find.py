import os

from asset_core.asset.asset_class import AssetClass
from asset_core.asset.asset_version import AssetVersion
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.server import AssetServer
from asset_utils.common import exceptions
from asset_utils.utils.log_utils import comma_formatted, kilo_byte
from .store import StoreAPI


class FindAPI(StoreAPI):

    def run(self, args):
        pass

    def find_asset(self, **kwargs):
        """Attempts to find the name an asset based on provided search criteria.

        Parameters
        ----------
        **kwargs : dict
            Search criteria including alias, version names, class name, and commit hash.

        Returns
        -------
        str or None
            The name of the found asset without its version, or None if not found.

        Raises
        ------
        exceptions.AssetException
            If an error occurs during the asset search.
        """
        server_access = os.getenv("ASSET_SERVER_ACCESS") == "true"
        try:
            if kwargs.get("alias"):
                asset_name = self.find_asset_alias_from_bucket(alias=kwargs.get("alias"),
                                                               class_name=kwargs.get("class_name"),
                                                               class_id=kwargs.get("class_id"))
                if asset_name:
                    return asset_name
                # if server access is disabled, return None
                if not server_access:
                    question = (f"asset with alias: {kwargs.get('alias')} not found in cloud storage,"
                                f" do you want to check in asset-server?")
                    user_input = self.user_log.ask_user(question=question, options=["y", "n"], default="n")
                    if user_input.lower() != "y":
                        return None

                asset_name = AssetServer().find_asset(**kwargs)
                # strip version
                if asset_name:
                    if "/" in asset_name:
                        comps = asset_name.split("/")
                        name = "/".join(comps[:-1])
                        return name
                    return asset_name
            else:
                # need server access for the rest as we only store alias in the bucket
                versions = AssetServer().find_asset_versions(project_id=self.store.project_id,
                                                             version_names=kwargs.get("version_names"),
                                                             class_name=kwargs.get("class_name"),
                                                             commit_hash=kwargs.get("hash"))
                return ",".join(versions) if versions else None
        except exceptions.AssetException as e:
            e.logs.add(e.msg, e.log_colors.ERROR)
            e.msg = "can not find asset"
            raise e from e

    def find_asset_alias_from_bucket(self, alias: str, class_name=None, class_id=None) -> str:
        """Finds the asset name from the bucket using the alias.

        Parameters
        ----------
        alias : str
            The alias of the asset.
        class_name : str, optional
            The name of the asset class.
        class_id : str, optional
            The id of the asset class.

        Returns
        -------
        str
            The name of the asset in <class_name>/<seq_id> format.

        Raises
        ------
        exceptions.AssetException
            If an error occurs during the asset search.
        exceptions.AssetClassNotFoundError
            If the asset class is not found.
        """
        if not class_name and not class_id:
            raise exceptions.AssetException("class_name or class_id not provided")

        if class_name and class_id:
            class_data = {"id": class_id, "name": class_name}
        else:
            class_data = self.find_asset_class_from_bucket(class_name=class_name, class_id=class_id)
        # get seq_id from bucket using alias
        seq_id = AssetFetcher(store=self.store).get_seq_id_from_bucket(class_id=class_data.get("id"), alias=alias)
        return f"{class_data.get('name')}/{seq_id}" if seq_id else None

    def find_asset_class_from_bucket(self, class_name=None, class_id=None) -> dict:
        """Finds the asset class data from the bucket."""
        try:
            # try getting from local cache
            class_data = AssetClass.cached_class_data(store=self.store, id=class_id, name=class_name)
        except exceptions.AssetException:
            self.user_log.message(f"asset-class: {class_name or class_id} not found locally, checking in remote")
            # fetch from remote
            AssetFetcher(store=self.store).fetch_asset_class(class_id=class_id, class_name=class_name)
            class_data = AssetClass.cached_class_data(store=self.store, id=class_id, name=class_name)

        if not class_data:
            raise exceptions.AssetClassNotFoundError(
                f"invalid class name or id, no asset-class found for {class_name or class_id}")
        return class_data

    def find_asset_size(self, asset_version_name: str = None, jsonize: bool = False):
        """Finds the size of a specified asset version from server. If version_name is missing, it defaults to latest
        version
        - we first look for the version data in bucket, since the data is cached there
        - if version-data in bucket doesn't have size or size is null, we fetch the data from server
        - this could happen because we added the size field later and data might not have been fully migrated to bucket

        Parameters
        ----------
        asset_version_name : str
            The name of the asset version in the format <class_name>/<seq_id>/<version>.
        jsonize: bool
            If true, returns the size as is, else prints the size in user-friendly manner

        Returns
        -------
        int
            The size of the asset version.

        Raises
        ------
        exceptions.InvalidAssetNameError
            If the asset version name format is incorrect.
        exceptions.AssetNotFoundError
            If the asset version is not found.
        exceptions.AssetException
            If an error occurs during the asset search.
        """
        server_access = os.getenv("ASSET_SERVER_ACCESS") == "true"
        comps = AssetVersion.parse_name(asset_version_name, default_to_root=False)
        if not comps or not comps.get("class_name"):
            raise exceptions.InvalidAssetNameError(
                "Invalid asset version name, expected <class_name>/<seq_id>/<version>")
        class_data = self.find_asset_class_from_bucket(class_name=comps.get("class_name"))
        if not class_data:
            raise exceptions.AssetClassNotFoundError(f"asset class not found: {comps.get('class_name')}")

        self.user_log.message(f"found asset-class: {class_data.get('name')} with id: {class_data.get('id')}")
        comps["class_id"] = class_data.get("id")

        # user might have passed alias, find seq_id from bucket
        if comps.get("alias"):
            asset_name = self.find_asset_alias_from_bucket(alias=comps.get("alias"),
                                                           class_name=class_data.get("name"),
                                                           class_id=class_data.get("id"))
            if not asset_name:
                if not server_access:
                    question = (f"asset with alias: {comps.get('alias')} not found in cloud storage,"
                                f" do you want to check in asset-server?")
                    user_input = self.user_log.ask_user(question=question, options=["y", "n"], default="n")
                    if user_input.lower() != "y":
                        return None
                # try to get the alias from server
                asset_name = AssetServer().find_asset(alias=comps.get("alias"), class_id=comps.get("class_id"))
                if not asset_name:
                    raise exceptions.AssetNotFoundError(f"can not find asset with alias: {comps.get('alias')}")

            self.user_log.message(f"found asset with alias:{comps.get('alias')} as {asset_name}")
            comps["seq_id"] = asset_name.split("/")[-1]

        # find size from bucket
        version_data = AssetFetcher(store=self.store).get_version_from_bucket(class_id=comps.get("class_id"),
                                                                              seq_id=comps.get("seq_id"),
                                                                              ver_number=comps.get("version"))
        if not version_data:
            raise exceptions.AssetNotFoundError(f"can not find asset: {asset_version_name}")

        # 0 is valid size, so we need to check if size is None
        if version_data.get("size") is None:
            # try to get it from server
            self.user_log.message("found version data in cloud storage but size is missing")
            if not server_access:
                question = "do you want to fetch the size from asset-server?"
                user_input = self.user_log.ask_user(question=question, options=["y", "n"], default="n")
                if user_input.lower() != "y":
                    return None

            self.user_log.message(f"fetching size from server for: {asset_version_name}")
            try:
                version_data = AssetServer().get_version(project_id=self.store.project_id,
                                                         class_id=comps.get("class_id"),
                                                         seq_id=comps.get("seq_id"),
                                                         version_number=comps.get("version"))
                if not version_data:
                    raise exceptions.AssetNotFoundError(f"can not find asset: {asset_version_name}")

            except exceptions.AssetException as e:
                e.logs.add(e.msg, e.log_colors.ERROR)
                e.msg = "can not find asset"
                raise e from e

        if version_data:
            msg = f"success: found version data for: {asset_version_name}"
            if version_data.get("size") is None:
                msg += " - but size is None"
            self.user_log.info(msg)

        asset_size = version_data.get("size")
        if jsonize:
            return asset_size

        # CLI invoked, so we need to print in user-friendly manner
        asset_name = '/'.join([comps.get('class_name'), comps.get('seq_id'), version_data.get('number')])
        if not comps.get("version"):
            asset_name = f"{asset_name} (latest)"  # tell the user that this is the latest version
        if asset_size is None:
            self.user_log.error(f"size is not available asset: {asset_name}")
        else:
            size = f"{comma_formatted(kilo_byte(asset_size))} KB"
            self.user_log.message(f"{asset_name} size: {size}", formatted=False)
