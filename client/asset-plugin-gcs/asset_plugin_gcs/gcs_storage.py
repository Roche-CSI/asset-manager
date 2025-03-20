import os
from typing import Type, Union

from asset_contents import BlobStoreContent
from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.object_content import ObjectContent
from asset_pluggy.storage import BlobStoreURL, StorageURL, StorageData
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_pluggy.storage.transporter import Transporter
from asset_plugin_gcs.bucket_cors import get_bucket_cors, update_cors_configuration
from asset_plugin_gcs.gcs_blob import GcsBlob
from asset_plugin_gcs.gcs_storage_mixin import GcsStorageMixin
from asset_plugin_gcs.signed_url import generate_signed_url
from asset_plugin_gcs.transporter import AsyncGcsTransporter
from asset_utils.common import exceptions


class GcsStorage(AssetStorage, GcsStorageMixin):
    prefixes = ["gs://"]
    name = "gs"

    def allows_object_add(self):
        return True

    def allows_proxy(self):
        return True

    def get_transporter(self) -> Transporter:
        return AsyncGcsTransporter.shared(credentials=self.credentials)

    def get_content_class(self) -> Type[ObjectContent]:
        return BlobStoreContent

    def get_object_path(self, asset_root: str, blob: StorageData, parent_url: StorageURL) -> str:
        if parent_url.dir_name and not blob.name.startswith(parent_url.dir_name):
            raise exceptions.InvalidObjectSourceError(f"{blob.name} is outside {parent_url.dir_name}")
        return os.path.relpath(blob.name, parent_url.dir_name)

    def get_storage_url(self, url_string: str, ignore: str = None) -> StorageURL:
        return BlobStoreURL(url=url_string, ignore=ignore)

    def get_blob(self, url_string: str) -> GcsBlob:
        """Returns a GcsBlob instance located at the url."""
        gcs_url = BlobStoreURL(url=url_string)
        return GcsBlob(data=self.fetch_blob_data(url=gcs_url), url_object=gcs_url)

    def blob_exists(self, url_string: str) -> bool:
        """Checks if a blob exists at the given URL."""
        return self.check_if_blob_exists(url=BlobStoreURL(url=url_string))

    def list_blobs(self, url: Union[StorageURL, str], ignore: str = None) -> [GcsBlob]:
        """Returns a list of GcsBlobs located at the url.

        Parameters
        ----------
        url : Union[str, StorageURL]
            The URL.
        ignore : str, optional
            The ignore string.

        Returns
        -------
        list
            A list of GcsBlob instances.
        """
        if type(url) is str:
            url = BlobStoreURL(url=url, ignore=ignore)
        blob_list = self.fetch_blobs_list(url=url)
        return list(map(lambda x: GcsBlob(data=x, url_object=url), blob_list))

    def delete_blobs(self, url_strings: [str]) -> None:
        self._delete_blob_urls(urls=list(map(lambda x: BlobStoreURL(url=x), url_strings)))

    def url_is_file(self, url: Union[StorageURL, str]) -> bool:
        """Checks if the URL is a file.

        Parameters
        ----------
        url : Union[StorageURL, str]
            The URL to check.

        Returns
        -------
        bool
            True if the URL is a file, False otherwise.
        """
        if type(url) is str:
            url = BlobStoreURL(url=url)
        # Blobs are files, so if a blob exists then it's a file else either the url doesn't exist or it's a directory
        return self.blob_exists(url_string=url.url)

    def filter_duplicate_blobs(self, src_blobs: [StorageData], dst_blobs: [StorageData]) -> (list, list):
        """Filters the source blobs to determine which blobs are new and which need to be replaced in the destination.

        If a blob in `src_blobs` has the same path_in_asset as a blob in `dst_blobs`, it compares their hashes.
        If the hashes are different, the blob is added to the replace_blobs list. If the path_in_asset is not
        found in `dst_blobs`, the blob is considered new and is added to the new_blobs list.

        Parameters
        ----------
        src_blobs : list
            A list of source blobs.
        dst_blobs : list
            A list of destination blobs.

        Returns
        -------
        tuple
            A tuple containing two lists: new_blobs and replace_blobs. new_blobs is a list of blobs that are new and
            replace_blobs is a list of blobs that need to be replaced in the destination.
        """
        if not dst_blobs:  # nothing to filter against
            return src_blobs, []
        new_blobs, replace_blobs = [], []
        # compare the path_in_asset and hash of the blobs
        dst_blob_map = {obj.path_in_asset: obj for obj in dst_blobs}
        for src_blob in src_blobs:
            if src_blob.path_in_asset in dst_blob_map:
                # need to compare hash and replace if different
                remote_blob = src_blob
                posix_blob = dst_blob_map[src_blob.path_in_asset]
                if isinstance(posix_blob, GcsBlob):
                    posix_blob, remote_blob = remote_blob, posix_blob
                # always invoke compare_hash method on PosixBlob
                if not posix_blob.compare_hash(remote_blob):
                    replace_blobs.append(src_blob)
            else:
                # new path_in_asset new object
                new_blobs.append(src_blob)
        return new_blobs, replace_blobs

    # used in asset-server
    def signed_url_for_blob(self, blob_url: str):
        gcs_url = BlobStoreURL(url=blob_url)
        return generate_signed_url(service_account_json=self.credentials,
                                   bucket_name=gcs_url.bucket,
                                   object_name=gcs_url.path)

    # used in asset-server
    def get_bucket_cors(self, bucket_url: str):
        url = BlobStoreURL(url=bucket_url)
        return get_bucket_cors(credentials=self.credentials, bucket_name=url.bucket)

    # used in asset-server
    def set_bucket_cors(self, bucket_url: str, origin_url):
        url = BlobStoreURL(url=bucket_url)
        return update_cors_configuration(credentials=self.credentials,
                                         bucket_name=url.bucket,
                                         origin_url=origin_url)


class GcsStoragePlugin:
    @hook_impl
    def asset_storage_get(self) -> Type[AssetStorage]:
        return GcsStorage
