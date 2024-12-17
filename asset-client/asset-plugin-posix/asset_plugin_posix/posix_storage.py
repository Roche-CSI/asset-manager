import os
from typing import Type, Union

from asset_contents import PosixContent
from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.object_content import ObjectContent
from asset_pluggy.storage import StorageData
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_pluggy.storage.transporter import Transporter
from asset_plugin_posix.posix_blob import PosixBlob
from asset_plugin_posix.posix_mixin import PosixStorageMixin
from asset_plugin_posix.posix_url import PosixURL, StorageURL
from asset_plugin_posix.transporter.async_posix_transporter import AsyncPosixTransporter
from asset_utils.common import exceptions


class PosixStorage(AssetStorage, PosixStorageMixin):
    prefixes = ["file://"]
    name = "posix"

    def allows_proxy(self):
        # proxy not allowed from local
        return False

    def allows_object_add(self):
        return True

    def get_storage_url(self, url_string: str, ignore: str = None) -> PosixURL:
        return PosixURL(url=url_string, ignore=ignore)

    def get_content_class(self) -> Type[ObjectContent]:
        return PosixContent

    def get_object_path(self, asset_root: str, blob: StorageData, parent_url: StorageURL) -> str:
        if not str(blob.name).startswith(asset_root):
            raise exceptions.InvalidObjectSourceError(msg=f"outside repo: {blob.name}")
        return os.path.relpath(path=blob.name, start=asset_root)

    def get_transporter(self) -> Transporter:
        return AsyncPosixTransporter.shared()

    def get_blob(self, url_string: str) -> PosixBlob:
        """Get blob from posix url

        Parameters
        ----------
        url_string : str
            posix url string

        Returns
        -------
        PosixBlob
            posix blob object
        """
        psx_url = PosixURL(url=url_string)
        return PosixBlob(data=self.fetch_blob_data(url=psx_url), url_object=psx_url)

    def blob_exists(self, url_string: str) -> bool:
        """Check if blob exists

        Parameters
        ----------
        url_string : str
            posix url string

        Returns
        -------
        bool
            True if blob exists, False otherwise
        """
        return self.check_if_blob_exists(url=PosixURL(url=url_string))

    def blobs_exist(self, url_string: str) -> dict:
        raise NotImplementedError

    def list_blobs(self, url: Union[str, StorageURL], ignore: str = None) -> [StorageData]:
        """List blobs from posix url

        Parameters
        ----------
        url : Union[str, StorageURL]
            posix url
        ignore : str
            ignore pattern

        Returns
        -------
        [StorageData]
            list of posix blobs
        """
        if type(url) is str:
            url = PosixURL(url=url, ignore=ignore)
        data: list = self.fetch_blobs_list(url=url)
        return list(map(lambda item: PosixBlob(data=item, url_object=url), data))

    def delete_blobs(self, url_strings: [str]) -> None:
        self._delete_blob_urls(urls=list(map(lambda x: PosixURL(url=x), url_strings)))

    def url_is_file(self, url: Union[str, StorageURL]) -> bool:
        """Check if url is a file

        Parameters
        ----------
        url : Union[str, StorageURL]
            posix url

        Returns
        -------
        bool
            True if url is a file, False otherwise
        """
        if type(url) is str:
            url = PosixURL(url=url)
        return os.path.isfile(url.url)

    def filter_duplicate_blobs(self, src_blobs: [StorageData], dst_blobs: [StorageData]):
        raise NotImplementedError


class PosixStoragePlugin:
    @hook_impl
    def asset_storage_get(self) -> Type[AssetStorage]:
        return PosixStorage
