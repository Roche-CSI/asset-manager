import os
from functools import cached_property
from typing import Union

from asset_pluggy.storage import StorageData, StorageURL, BlobStoreURL, storage_utils
from asset_pluggy.storage.mount_config import MountConfig
from asset_plugin_s3.aws_blob import AwsBlob
from asset_plugin_s3.mounted_bucket.async_mount_transporter import AsyncMountTransporter
from asset_plugin_s3.mounted_bucket.mounted_url import MountedBlobStoreURL
from asset_plugin_s3.s3_proxy import S3Proxy
from asset_utils.common import exceptions


class AwsMountHandler:
    """AWS Mount Handler class for handling AWS S3 using mounted directories."""

    def __init__(self, config: MountConfig):
        self.mount_config = config

    def get_transporter(self) -> AsyncMountTransporter:
        return AsyncMountTransporter.shared(mount_cfg=self.mount_config)

    @cached_property
    def s3_service(self):
        backend_url = os.getenv("ASSET_SERVER_URL")
        if not backend_url:
            raise exceptions.ServerUrlNotSetError("asset-server URL is not set")

        return S3Proxy(backend_url)

    def allows_object_add(self):
        """Checks if object addition is allowed."""
        return True

    def allows_proxy(self):
        """Checks if proxy is allowed."""
        return True

    def get_storage_url(self, url_string: str, ignore: str = None) -> StorageURL:
        return BlobStoreURL(url=url_string, ignore=ignore)

    def get_blob(self, url_string: str) -> AwsBlob:
        """Get the blob instance from the given URL.

        Fetch the blob data through asset server and convert to AwsBlob.
        This only contains blob metadata not the content.
        """
        aws_url = BlobStoreURL(url=url_string)
        # fetch blob data through server
        blob_data = self.s3_service.get_object(aws_url.url)
        # convert blob data to AwsBlob
        return AwsBlob(data=blob_data, url_object=aws_url)

    def blob_exists(self, url_string: str) -> bool:
        """Checks if a blob exists at the given URL.

        Instead of checking in the server, we check if the blob exists in the mounted directory.
        """
        mount_url = MountedBlobStoreURL(url=url_string, mount_cfg=self.mount_config)
        return os.path.exists(mount_url.posix_url)

    def url_is_file(self, url: Union[StorageURL, str]) -> bool:
        """Checks if the URL is a file.

        Instead of checking in the server, we check if the blob exists in the mounted directory.
        """
        if type(url) is not str:
            url = url.url
        mount_url = MountedBlobStoreURL(url=url, mount_cfg=self.mount_config)
        return os.path.isfile(mount_url.posix_url)

    def list_blobs(self, url: Union[str, StorageURL], ignore: str = None) -> [AwsBlob]:
        """List the AwsBlob instances from the given URL.

        Fetch the list of blob data through asset server and convert to AwsBlob.
        This only contains blob metadata not the content.
        """
        if type(url) is str:
            url = BlobStoreURL(url=url, ignore=ignore)
        return self.fetch_blobs_list(url=url)

    def fetch_blobs_list(self, url: BlobStoreURL) -> list:
        # fetch list through server
        objects = self.s3_service.list_objects(url.url)
        # convert list of dict to list of AwsBlob
        blobs = [AwsBlob(data=object_data, url_object=url) for object_data in objects]
        # pattern is already included in the url so just filter ignore
        return storage_utils.filter_blobs(blobs=blobs, name_key="name", ignore=url.ignore)

    def delete_blobs(self, url_strings: [str]):
        raise NotImplementedError

    def filter_duplicate_blobs(self, src_blobs: [StorageData], dst_blobs: [StorageData]):
        # TODO: May be we can return everything as new blobs
        # since we can not check for duplicates in mounted directories.
        raise NotImplementedError
