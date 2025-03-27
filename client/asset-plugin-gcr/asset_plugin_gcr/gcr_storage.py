from typing import Type, Union

from asset_contents import DockerContent
from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.object_content import ObjectContent
from asset_pluggy.storage import StorageData, StorageURL, Transporter
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_plugin_gcr.gcr_blob import GcrBlob
from asset_plugin_gcr.gcr_mixin import GcrMixin
from asset_plugin_gcr.gcr_url import GcrURL
from asset_plugin_gcr.transporter.gcr_transporter import GcrTransporter


class GcrStorage(AssetStorage, GcrMixin):
    prefixes = ["gcr.io/", "us.gcr.io/"]
    name = "gcr"

    def allows_proxy(self):
        return True

    def allows_object_add(self):
        return True

    def get_storage_url(self, url_string: str, ignore: str = None) -> StorageURL:
        return GcrURL(url=url_string, ignore=ignore)

    def get_transporter(self) -> Type[Transporter]:
        return GcrTransporter.shared()

    def get_content_class(self) -> Type[ObjectContent]:
        return DockerContent

    def get_object_path(self, asset_root: str, blob: GcrBlob, parent_url: StorageURL) -> str:
        return "-".join([*(blob.name.split("/")), *blob.get_hash()])

    def get_blob(self, url: str) -> GcrBlob:
        gcr_url: GcrURL = GcrURL(url=url)
        data = self.get_gcr_blob(url=gcr_url)
        return GcrBlob(data=data, url_object=gcr_url)

    def blob_exists(self, url_string: str) -> bool:
        raise NotImplementedError

    def list_blobs(self, url: Union[StorageURL, str], ignore: str = None) -> [StorageData]:
        if type(url) is str:
            url = GcrURL(url=url, ignore=ignore)
        data = self.get_gcr_blob(url=url)
        return [GcrBlob(data=data, url_object=url)]

    def delete_blobs(self, url_strings: [str]) -> None:
        # delete not allowed in gcr currently
        raise NotImplementedError


class GcrStoragePlugin:
    @hook_impl
    def asset_storage_get(self) -> Type[AssetStorage]:
        return GcrStorage
