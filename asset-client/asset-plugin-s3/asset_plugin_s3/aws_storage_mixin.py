from functools import cached_property
from typing import Union

from asset_pluggy.storage import StorageData, StorageURL
from asset_plugin_s3.aws_http_handler import AwsHttpHandler
from asset_plugin_s3.aws_mount_handler import AwsMountHandler


class AwsStorageMixin:

    @cached_property
    def s3_handler(self):
        # self.mount_config is set by the StorageFactory
        if self.mount_config:
            return AwsMountHandler(config=self.mount_config)
        else:
            return AwsHttpHandler(credentials=self.credentials)

    def get_transporter(self):
        return self.s3_handler.get_transporter()

    def allows_object_add(self):
        return self.s3_handler.allows_object_add()

    def allows_proxy(self):
        return self.s3_handler.allows_proxy()

    def get_storage_url(self, url_string: str, ignore: str = None) -> StorageURL:
        return self.s3_handler.get_storage_url(url_string=url_string, ignore=ignore)

    def get_blob(self, url_string: str) -> StorageData:
        return self.s3_handler.get_blob(url_string=url_string)

    def blob_exists(self, url_string: str) -> bool:
        return self.s3_handler.blob_exists(url_string=url_string)

    def url_is_file(self, url: Union[StorageURL, str]) -> bool:
        return self.s3_handler.url_is_file(url=url)

    def list_blobs(self, url: Union[str, StorageURL], ignore: str = None) -> [StorageData]:
        return self.s3_handler.list_blobs(url=url, ignore=ignore)

    def delete_blobs(self, url_strings: [str]) -> None:
        self.s3_handler.delete_blobs(url_strings=url_strings)
