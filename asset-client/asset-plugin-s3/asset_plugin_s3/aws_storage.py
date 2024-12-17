import os
from typing import Type

from asset_contents import BlobStoreContent
from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.object_content import ObjectContent
from asset_pluggy.storage import StorageData, StorageURL
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_plugin_s3.aws_storage_mixin import AwsStorageMixin
from asset_utils.common import exceptions


class AwsStorage(AwsStorageMixin, AssetStorage):
    prefixes = ["s3://"]
    name = "s3"

    def get_content_class(self) -> Type[ObjectContent]:
        """Returns the BlobStoreContent class.

        This method is used to get the class that represents the content of a blob in the storage.

        Returns
        -------
        Type[ObjectContent]
            The BlobStoreContent class.
        """
        return BlobStoreContent

    def get_object_path(self, asset_root: str, blob: StorageData, parent_url: StorageURL) -> str:
        """Returns the relative path of the blob from the asset root.

        Parameters
        ----------
        asset_root : str
            The root of the asset.
        blob : StorageData
            The blob.
        parent_url : StorageURL
            The parent URL.

        Returns
        -------
        str
            The relative path of the blob.

        Raises
        ------
        InvalidObjectSourceError
            If the blob name does not start with the directory name of the parent URL.
        """
        if not blob.name.startswith(parent_url.dir_name):
            raise exceptions.InvalidObjectSourceError(f"{blob.name} is outside {parent_url.dir_name}")
        return os.path.relpath(blob.name, parent_url.dir_name)


class AwsStoragePlugin:
    @hook_impl
    def asset_storage_get(self) -> Type[AssetStorage]:
        """Returns the AwsStorage class.

        This method is implemented as a hook for the pluggy plugin system. It returns the AwsStorage class,
        which is used by the plugin system to handle AWS S3 operations.

        Returns
        -------
        Type[AssetStorage]
            The AwsStorage class.
        """
        return AwsStorage
