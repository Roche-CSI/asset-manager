import aiohttp

from asset_pluggy.storage.transporter import Transporter, TransportResource
from asset_plugin_gcs.transporter.async_gcs import async_upload, async_download, async_copy
from asset_plugin_gcs.transporter.gcs_transport_resource import GcsUploadResource, GcsDownloadResource, GcsCopyResource
from asset_utils.common import exceptions
from asset_utils.utils import utils


class AsyncGcsTransporter(Transporter):
    def get_download_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return GcsDownloadResource(src=src, dst=dst, hash=src_hash)

    def get_upload_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return GcsUploadResource(src=src, dst=dst, hash=src_hash)

    def get_copy_resource(self, src: str, dst: str, src_hash: tuple, **kwargs) -> TransportResource:
        return GcsCopyResource(src=src, dst=dst, hash=src_hash, **kwargs)

    def upload(self, resources: [TransportResource]):
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_upload.upload_resources(credentials=self.credentials, resources=chunk)
        except exceptions.AssetException:
            raise
        except Exception as e:
            if isinstance(e, aiohttp.ClientResponseError) and e.status == 403:
                raise exceptions.InvalidStorageCredentialsError() from e
            raise exceptions.AssetException("Error while uploading resources") from e

    def download(self, resources: [TransportResource]):
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_download.download_resources(credentials=self.credentials, resources=chunk)
        except exceptions.AssetException:
            raise
        except Exception as e:
            if isinstance(e, aiohttp.ClientResponseError) and e.status == 403:
                raise exceptions.InvalidStorageCredentialsError() from e
            raise exceptions.AssetException("Error while downloading resources") from e

    def copy(self, resources: [TransportResource]):
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_copy.copy_resources(credentials=self.credentials, resources=chunk)
        except exceptions.AssetException:
            raise
        except Exception as e:
            if isinstance(e, aiohttp.ClientResponseError) and e.status == 403:
                raise exceptions.InvalidStorageCredentialsError() from e
            raise exceptions.AssetException("Error while copying resources") from e
