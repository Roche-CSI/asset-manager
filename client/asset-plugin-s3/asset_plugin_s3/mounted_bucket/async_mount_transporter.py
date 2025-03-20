from botocore.exceptions import ClientError

from asset_pluggy.storage.transporter import Transporter, TransportResource
from asset_plugin_s3.mounted_bucket import async_mount_copy
from asset_plugin_s3.mounted_bucket.mounted_resource import AwsMountedResource
from asset_utils.common import exceptions
from asset_utils.utils import utils


class AsyncMountTransporter(Transporter):
    mount_cfg = None

    @classmethod
    def shared(cls, mount_cfg=None, **kwargs):
        if not hasattr(cls, 'instance'):
            instance = super(AsyncMountTransporter, cls).shared(**kwargs)
            instance.mount_cfg = mount_cfg
            cls.instance = instance
        return cls.instance

    def get_download_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return AwsMountedResource(src=src, dst=dst, src_hash=src_hash, mount_cfg=self.mount_cfg)

    def get_upload_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return AwsMountedResource(src=src, dst=dst, src_hash=src_hash, mount_cfg=self.mount_cfg)

    def get_copy_resource(self, src: str, dst: str, src_hash: tuple, **kwargs) -> TransportResource:
        return AwsMountedResource(src=src, dst=dst, src_hash=src_hash, mount_cfg=self.mount_cfg, **kwargs)

    def upload(self, resources: [TransportResource]) -> None:
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_mount_copy.copy_resources(resources=chunk)
        # keep the exception handling as is, since fuse-mounting uses http under the hood
        except ClientError as e:
            if e.response["Error"]["Code"] == "SignatureDoesNotMatch":
                raise exceptions.InvalidStorageCredentialsError("Credentials expired. Fetch Again.") from e
            if e.response["Error"]["Code"] == "AccessDenied":
                raise exceptions.InsufficientCredentialError("Do not have access to upload resources") from e
            raise exceptions.AssetException("Client error while uploading resources") from e
        except Exception as e:
            raise exceptions.AssetException("Error while uploading resources") from e

    def download(self, resources: [TransportResource]) -> None:
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_mount_copy.copy_resources(resources=chunk)
        except Exception as e:
            if isinstance(e, ClientError) and e.response["Error"]["Code"] == "SignatureDoesNotMatch":
                raise exceptions.InvalidStorageCredentialsError("Credentials expired. Fetch Again.") from e
            raise exceptions.AssetException("Error while downloading resources") from e

    def copy(self, resources: [TransportResource]) -> None:
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_mount_copy.copy_resources(resources=chunk)
        except Exception as e:
            if isinstance(e, ClientError) and e.response["Error"]["Code"] == "SignatureDoesNotMatch":
                raise exceptions.InvalidStorageCredentialsError("Credentials expired. Fetch Again.") from e
            raise exceptions.AssetException("Error while copying resources") from e
