from botocore.exceptions import ClientError

from asset_pluggy.storage.transporter import Transporter, TransportResource
from asset_plugin_s3.transporter.async_aws import async_upload, async_download, async_copy, async_update_blob
from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource, AwsDownloadResource, AwsCopyResource
from asset_utils.common import exceptions
from asset_utils.utils import utils


class AsyncAwsTransporter(Transporter):

    def get_download_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return AwsDownloadResource(src=src, dst=dst, hash=src_hash)

    def get_upload_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return AwsUploadResource(src=src, dst=dst, hash=src_hash)

    def get_copy_resource(self, src: str, dst: str, src_hash: tuple, **kwargs) -> TransportResource:
        return AwsCopyResource(src=src, dst=dst, hash=src_hash, **kwargs)

    def upload(self, resources: [TransportResource]) -> None:
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_upload.upload_resources(credentials=self.credentials, resources=chunk)
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
                async_download.download_resources(credentials=self.credentials, resources=chunk)
        except Exception as e:
            if isinstance(e, ClientError) and e.response["Error"]["Code"] == "SignatureDoesNotMatch":
                raise exceptions.InvalidStorageCredentialsError("Credentials expired. Fetch Again.") from e
            raise exceptions.AssetException("Error while downloading resources") from e

    def copy(self, resources: [TransportResource]) -> None:
        # update multipart sizes of resource if it has a blob
        self.update_multipart_sizes(resources=resources)
        try:
            for chunk in utils.batch(resources, batch_size=self.batch_size):
                async_copy.copy_resources(credentials=self.credentials, resources=chunk)
        except Exception as e:
            if isinstance(e, ClientError) and e.response["Error"]["Code"] == "SignatureDoesNotMatch":
                raise exceptions.InvalidStorageCredentialsError("Credentials expired. Fetch Again.") from e
            raise exceptions.AssetException("Error while copying resources") from e

    def update_multipart_sizes(self, resources: [AwsCopyResource]) -> None:
        blobs = [resource.blob for resource in resources if hasattr(resource, "blob") and resource.blob.is_multipart]
        if not blobs:
            return
        # fetch and update multipart sizes of blobs
        self.update_multipart_blobs(blobs=blobs)

    def update_multipart_blobs(self, blobs: list) -> None:
        try:
            for chunk in utils.batch(blobs, batch_size=self.batch_size):
                async_update_blob.update_multipart_sizes(credentials=self.credentials, blobs=chunk)
        except Exception as e:
            if isinstance(e, ClientError) and e.response["Error"]["Code"] == "SignatureDoesNotMatch":
                raise exceptions.InvalidStorageCredentialsError("Credentials expired. Fetch Again.") from e
            raise exceptions.AssetException("Error while fetching blob multipart size") from e
