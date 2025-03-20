from asset_plugin_s3.mounted_bucket.mounted_url import MountedBlobStoreURL
from asset_plugin_s3.transporter.aws_transport_resource import AwsDownloadResource


class AwsMountedResource(AwsDownloadResource):
    def __init__(self, src: str, dst: str, src_hash: tuple, **kwargs):
        self.mount_cfg = kwargs.pop("mount_cfg", None)
        super().__init__(src=src, dst=dst, hash=src_hash, **kwargs)

    @property
    def src_url(self) -> MountedBlobStoreURL:
        return MountedBlobStoreURL(url=self.src, mount_cfg=self.mount_cfg)

    @property
    def dst_url(self) -> MountedBlobStoreURL:
        return MountedBlobStoreURL(url=self.dst, mount_cfg=self.mount_cfg)

    def on_transfer_complete(self, *args):
        if self.callback:
            self.callback(*args)
