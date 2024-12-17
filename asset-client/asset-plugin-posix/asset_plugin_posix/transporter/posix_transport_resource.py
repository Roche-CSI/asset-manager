from cached_property import cached_property

from asset_pluggy.storage.transporter import TransportResource
from asset_plugin_posix.posix_url import PosixURL


class PosixUploadResource(TransportResource):
    @classmethod
    def from_transport_resource(cls, res: TransportResource):
        return PosixUploadResource(src=res.src, dst=res.dst, callback=res.callback)

    @cached_property
    def dst_url(self):
        return PosixURL(url=self.dst)


class PosixDownloadResource(TransportResource):
    @classmethod
    def from_transport_resource(cls, res: TransportResource):
        return PosixDownloadResource(src=res.src, dst=res.dst, callback=res.callback)

    @cached_property
    def src_url(self):
        return PosixURL(url=self.src)
