from __future__ import annotations

import os
from typing import TYPE_CHECKING

from asset_core.asset import AssetClass
from asset_core.asset.asset import Asset
from asset_core.asset.asset_version import AssetVersion
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.asset.status_enums import StatusEnums
from asset_core.plugins import exceptions
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin

if TYPE_CHECKING:
    from asset_core.api.store_api import FindAPI


class AssetHandle(LoggingMixin):

    def __init__(self,
                 class_id: str = None,
                 class_name: str = None,
                 seq_id: str = None,
                 version: str = None,
                 alias: str = None,
                 extras: str = None):
        self.class_id = class_id
        self.class_name = class_name
        self.seq_id = seq_id
        self.version = version
        self.alias = alias
        self.extras = extras

    @property
    def asset_name(self):
        if self.version:
            return AssetVersion.get_name(*[self.class_name, self.seq_id, self.version])
        else:
            return Asset.asset_name(class_name=self.class_name, seq_id=self.seq_id)

    @classmethod
    def from_name(cls, asset_name: str, version=None) -> AssetHandle:
        """Create an AssetHandle object from the asset name.

        Parameters
        ----------
        asset_name : str
            The name of the asset.
        version : str, optional
            The version of the asset.

        Returns
        -------
        AssetHandle
            The AssetHandle object.
        """
        parts = asset_name.split("/")
        if len(parts) < 2:
            raise exceptions.InvalidAssetNameError(f"invalid asset name: {asset_name}")
        # use the first two parts to get class_name and seq_id
        name_data = AssetVersion.parse_name(name=f"{parts[0]}/{parts[1]}", default_to_root=False)
        if len(parts) > 2:
            if AssetVersion.is_valid_format(ver_number=parts[2]):
                name_data["version"] = parts[2]
                name_data["extras"] = "/".join(parts[3:]) if len(parts) > 3 else None
            else:
                # if version is not valid, then it is part of extras
                name_data["extras"] = "/".join(parts[2:])
        # if user passed version, override the version from asset_name
        if version and AssetVersion.is_valid_format(ver_number=version):
            name_data["version"] = version
        return AssetHandle(**name_data)

    def fetch_and_update(self, fetcher: AssetFetcher, find_api: FindAPI) -> None:
        """Fetch and update the missing fields of the asset handle.

        Raises
        ------
        exceptions.AssetClassNotFoundError
            If the asset class is not found.
        exceptions.InvalidAssetNameError
            If the asset name is invalid.
        exceptions.InvalidAliasError
            If the alias is invalid.
        """
        # update class_id
        if not self.class_id:
            self.class_id = fetcher.get_asset_class_id(class_name=self.class_name)

        # if seq_id is provided, then nothing else to update
        if self.seq_id:
            return
        # if seq_id is not provided, then must provide alias
        if not self.alias:
            raise exceptions.InvalidAssetNameError(f"invalid asset-name: {self.class_name}")

        # search alias
        self.user_log.info(f"looking for asset with alias: {self.alias} in asset class: {self.class_name}")
        asset_name = find_api.find_asset(**{
            "class_name": self.class_name,
            "class_id": self.class_id,
            "alias": self.alias,
        })
        if not asset_name:
            raise exceptions.InvalidAliasError(f"invalid alias: {self.alias}")

        self.user_log.info(f"found asset: {asset_name}")
        # update seq_id
        self.update_seq_id(asset_name=asset_name)

    def update_seq_id(self, asset_name: str):
        """Update the seq_id from the asset_name"""
        temp = self.__class__.from_name(asset_name=asset_name)
        self.seq_id = temp.seq_id

    def is_valid(self, fetcher: AssetFetcher, find_api: FindAPI) -> bool:
        """Check if the asset handle has all necessary fields."""
        self.fetch_and_update(fetcher=fetcher, find_api=find_api)
        return bool(self.class_name and self.class_id and self.seq_id)

    def check_access_control(self, fetcher: AssetFetcher):
        """Check the status of the asset class and asset to determine access control."""
        try:
            # fetch the latest asset-class file for status check
            fetcher.download_asset_class(class_id=self.class_id)
        except exceptions.AssetException:
            if not os.path.exists(fetcher.store.asset_class_file(self.class_id)):
                raise exceptions.AssetException(f"failed to download the asset-class file: {self.class_id}")

        class_data = AssetClass.cached_class_data(store=fetcher.store, id=self.class_id)
        class_status = class_data.get("status", StatusEnums.default())
        if not StatusEnums.can_download(status=class_status, owner=class_data.get("owner")):
            raise exceptions.AssetException(
                f"asset class: {self.class_name} can not be cloned: {StatusEnums.to_string(class_status)}")

        # warn user if asset class is deprecated
        if class_status == StatusEnums.DEPRECATED:
            self.user_log.alert(f"Deprecated asset class: {self.class_name}")

        try:
            # fetch the latest asset.yaml file for status check
            fetcher.download_asset_file(class_id=self.class_id, seq_id=self.seq_id)
        except exceptions.AssetException:
            if not os.path.exists(fetcher.store.asset_file(self.class_id, self.seq_id)):
                raise exceptions.AssetException(f"failed to download the asset file: {self.class_name}/{self.seq_id}")

        asset_data = FileUtils.read_yaml(fetcher.store.asset_file(self.class_id, self.seq_id))
        asset_status = asset_data.get("status", StatusEnums.default())
        if not StatusEnums.can_download(status=asset_status, owner=asset_data.get("owner")):
            raise exceptions.AssetException(
                f"asset: {self.asset_name} can not be cloned: {StatusEnums.to_string(asset_status)}")

        # warn user if the asset is deprecated
        if asset_status == StatusEnums.DEPRECATED:
            self.user_log.alert(f"Deprecated asset: {self.asset_name}")

    def is_temp(self) -> bool:
        """Check if the asset is a local temporary asset."""
        return Asset.is_temp_seq_id(seq_id=self.seq_id)
