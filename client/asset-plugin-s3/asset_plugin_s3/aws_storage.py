import os
from typing import Type

from asset_contents import BlobStoreContent
from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.object_content import ObjectContent
from asset_pluggy.storage import StorageData, StorageURL, BlobStoreURL
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_plugin_s3.aws_storage_mixin import AwsStorageMixin
from asset_plugin_s3.bucket_cors import get_bucket_cors, set_bucket_cors
from asset_plugin_s3.signed_url import create_presigned_url
from asset_utils.common import exceptions


class AwsStorage(AwsStorageMixin, AssetStorage):
    prefixes = ["s3://"]
    name = "s3"

    def get_content_class(self) -> Type[ObjectContent]:
        """Returns the BlobStoreContent class."""
        return BlobStoreContent

    def get_object_path(self, asset_root: str, blob: StorageData, parent_url: StorageURL) -> str:
        """Returns the relative path of the blob from the asset root."""
        if not blob.name.startswith(parent_url.dir_name):
            raise exceptions.InvalidObjectSourceError(f"{blob.name} is outside {parent_url.dir_name}")
        return os.path.relpath(blob.name, parent_url.dir_name)

    # used in asset-server
    def signed_url_for_blob(self, blob_url: str):
        """Returns a signed URL for the given blob URL."""
        url = BlobStoreURL(url=blob_url)
        return create_presigned_url(credentials=self.credentials,
                                    bucket_name=url.bucket,
                                    object_name=url.path)

    # used in asset-server
    def get_bucket_cors(self, bucket_url: str):
        """Returns the CORS configuration for the given bucket URL."""
        url = BlobStoreURL(url=bucket_url)
        return get_bucket_cors(credentials=self.credentials,
                               bucket_name=url.bucket)

    # used in asset-server
    def set_bucket_cors(self, bucket_url: str, origin_url):
        """Sets the CORS configuration for the given bucket URL."""
        url = BlobStoreURL(url=bucket_url)
        return set_bucket_cors(credentials=self.credentials,
                               bucket_name=url.bucket,
                               origin_url=origin_url)


class AwsStoragePlugin:
    @hook_impl
    def asset_storage_get(self) -> Type[AssetStorage]:
        """Returns the AwsStorage class."""
        return AwsStorage
