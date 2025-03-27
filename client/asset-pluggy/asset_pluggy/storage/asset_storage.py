import abc
import os
from typing import Type, Union

from asset_pluggy.plugin.object_content import ObjectContent
from asset_pluggy.storage.blob import StorageData
from asset_pluggy.storage.mount_config import MountConfig
from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_pluggy.storage.transporter import Transporter
from asset_pluggy.storage.urls import StorageURL
from asset_utils.common import Singleton, exceptions
from asset_utils.utils.log_utils import LoggingMixin


class AssetStorage(Singleton, LoggingMixin):
    prefixes: [str] = []  # list of prefixes
    name: str = None

    def post_init(self):
        self.validate()

    def validate(self):
        # verify transporter (test if it's working)
        transporter = self.get_transporter()
        if not transporter or not isinstance(transporter, Transporter):
            raise exceptions.InvalidStorageBackendError("StorageBackend must provide a Transporter")
        # cleanup transporter
        transporter.de_init()

    @property
    def credentials(self) -> dict:
        return StorageCredentials.shared().credentials

    @property
    def mount_config(self) -> MountConfig:
        return getattr(self, "_mount_config", None)

    @mount_config.setter
    def mount_config(self, value: str):
        self._mount_config = value

    @abc.abstractmethod
    def get_storage_url(self, url_string: str, ignore: str = None) -> StorageURL:
        raise NotImplementedError

    @abc.abstractmethod
    def allows_proxy(self):
        """allows objects to be created from its url as proxy"""
        raise NotImplementedError

    @abc.abstractmethod
    def allows_object_add(self):
        """allows objects to be created from its url"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_blob(self, url_string: str) -> StorageData:
        raise NotImplementedError

    @abc.abstractmethod
    def blob_exists(self, url_string: str) -> bool:
        """check if the blob exists without downloading data"""
        raise NotImplementedError

    @abc.abstractmethod
    def list_blobs(self, url: Union[StorageURL, str], ignore: str = None) -> [StorageData]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_blobs(self, url_strings: [str]) -> None:
        """delete one or more blobs"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_transporter(self) -> Transporter:
        raise NotImplementedError

    @abc.abstractmethod
    def get_content_class(self) -> Type[ObjectContent]:
        raise NotImplementedError

    def parse_blobs_from_url(self,
                             repo_dir: str,
                             url_string: str,
                             ignore: str = None,
                             dest_dir: str = None) -> [tuple]:
        """parse the source of content creation

        Parameters
        ----------
        repo_dir: str
            Repo directory
        url_string: StorageURL
            url_object from which the blobs were collected
        ignore: str
            glob pattern
        dest_dir: str
            optional, if provided, a new dest_dir is added to the file path

        Returns
        -------
        [tuple]:
            ([(blob: StorageData, path: str)])

        """
        search_url: StorageURL = self.get_storage_url(url_string=url_string, ignore=ignore)
        blobs: [StorageData] = self.list_blobs(url=search_url)
        sources = []
        for blob in blobs:
            content_dst = self.get_object_path(asset_root=repo_dir, blob=blob, parent_url=search_url)
            if dest_dir:
                content_dst = os.path.join(dest_dir, content_dst)
            sources.append((blob, content_dst))
        return sources

    @abc.abstractmethod
    def get_object_path(self, asset_root: str, blob: StorageData, parent_url: StorageURL) -> str:
        """Returns the path where the blob would be mounted inside the asset

        Parameters
        ----------
        asset_root: str
            Repo directory path
        blob: StorageData
        parent_url: StorageURL

        Returns
        -------
        str:
            mounting path inside the asset

        """
        raise NotImplementedError

    @abc.abstractmethod
    def url_is_file(self, url: Union[StorageURL, str]):
        raise NotImplementedError

    # used in asset-server
    @abc.abstractmethod
    def signed_url_for_blob(self, blob_url: str):
        raise NotImplementedError

    # used in asset-server
    @abc.abstractmethod
    def set_bucket_cors(self, bucket_url: str, origin_url):
        raise NotImplementedError

    # used in asset-server
    @abc.abstractmethod
    def get_bucket_cors(self, bucket_url: str):
        raise NotImplementedError
