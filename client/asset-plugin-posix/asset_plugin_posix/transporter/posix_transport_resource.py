from cached_property import cached_property

from asset_pluggy.storage.transporter import TransportResource
from asset_plugin_posix.posix_url import PosixURL


class PosixTransportResource(TransportResource):
    """A class that represents a resource for POSIX transport operations."""

    @classmethod
    def from_transport_resource(cls, res: TransportResource):
        return cls(src=res.src, dst=res.dst, callback=res.callback)

    @cached_property
    def src_url(self):
        return PosixURL(url=self.src)

    @cached_property
    def dst_url(self):
        return PosixURL(url=self.dst)
