from asset_pluggy.storage.transporter import Transporter, TransportResource
from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource, AwsDownloadResource
from asset_plugin_s3.transporter.legacy_aws import async_upload, async_download
from asset_utils.utils import utils


class LegacyAwsTransporter(Transporter):
    def get_upload_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return AwsUploadResource(src=src, dst=dst, hash=src_hash)

    def get_download_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        return AwsDownloadResource(src=src, dst=dst, hash=src_hash)

    def upload(self, resources: [TransportResource]) -> None:
        for chunk in utils.batch(resources, batch_size=self.batch_size):
            async_upload.upload_resources(credentials=self.credentials, resources=chunk)

    def download(self, resources: [TransportResource]) -> None:
        for chunk in utils.batch(resources, batch_size=self.batch_size):
            async_download.download_resources(credentials=self.credentials, resources=chunk)
