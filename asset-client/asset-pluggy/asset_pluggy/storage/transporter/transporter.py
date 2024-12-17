import abc
import enum
import os

from asset_utils.common.singleton import Singleton
from .transport_resource import TransportResource

DEFAULT_TIMEOUT = 86400  # in seconds i.e. 24 hours (60 * 60 * 24)
DEFAULT_BATCH_SIZE = 400  # max 400 concurrent requests


class TransportOps(enum.Enum):
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    COPY = "COPY"


class Transporter(Singleton):
    credentials: dict = None
    prefixes: list = None  # storage system prefixes

    @classmethod
    def shared(cls, credentials: dict = None, prefixes: list = None):
        kwargs = {"credentials": credentials, "prefixes": prefixes}
        return super(Transporter, cls).shared(**kwargs)

    def post_init(self, **kwargs):
        self.credentials = kwargs.get("credentials")
        self.prefixes = kwargs.get("prefixes")

    @property
    def batch_size(self):
        return int(os.getenv("ASSET_BATCH_SIZE")) if os.getenv("ASSET_BATCH_SIZE") else DEFAULT_BATCH_SIZE

    def transfer(self, resources: [TransportResource]):
        """Generic interface for transferring from one source to another.
        This is meant to be the first landing point for all upload, download or copy
        operations:
            - upload: if dst has prefix but src doesn't
            - download: if src has prefix but dst doesn't
            - copy: if src and dst both have the prefixes

        Inheriting transporter classes can implement logic to determine which sub operation
        to invoke
        """
        copies, downloads, uploads = [], [], []
        for resource in resources:
            src_is_native = self.is_native_url(resource.src)
            dst_is_native = self.is_native_url(resource.dst)
            if src_is_native and dst_is_native:
                copies.append(resource)
            elif src_is_native:
                # src is already inside the transporter's native system, so we need to download
                downloads.append(resource)
            elif dst_is_native:
                uploads.append(resource)
        if copies:
            self.copy(resources=copies)
        if downloads:
            self.download(resources=downloads)
        if uploads:
            self.upload(resources=uploads)

    def get_download_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        raise NotImplementedError

    def get_upload_resource(self, src: str, dst: str, src_hash: tuple) -> TransportResource:
        raise NotImplementedError

    def get_copy_resource(self, src: str, dst: str, src_hash: tuple, **kwargs) -> TransportResource:
        raise NotImplementedError

    def is_native_url(self, url: str):
        for prefix in self.prefixes:
            if url.startswith(prefix):
                return True
        return False

    @abc.abstractmethod
    def upload(self, resources: [TransportResource]):
        """upload resources from src to dst"""
        raise NotImplementedError

    @abc.abstractmethod
    def download(self, resources: [TransportResource]):
        """download resources from src to dst"""
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self, resources: [TransportResource]):
        """copy resources from src to dst"""
        raise NotImplementedError

    def timeout(self) -> int:
        """returns the timeout for upload and download transactions"""
        return DEFAULT_TIMEOUT
