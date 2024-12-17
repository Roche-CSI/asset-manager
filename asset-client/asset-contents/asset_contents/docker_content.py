from __future__ import annotations

import aiohttp
import backoff

from asset_pluggy.storage.blob import StorageData
from asset_utils.common import exceptions
from asset_utils.utils import cloud_utils
from .content import Content


class DockerContent(Content):
    """Class to Manage Storage of docker contents"""

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        hash_value: str
            hash value of the object
        hash_type: str
            hash mime_type, default is md5
        """
        super().__init__(**self.validate_kwargs(kwargs))

    @classmethod
    def create(cls, storage_name: str,
               blob: StorageData,
               proxy: bool = True) -> DockerContent:
        """Create a new DockerContent object from a StorageData object"""
        hash_type, hash_value = blob.get_hash()
        return DockerContent(mime=blob.content_type,
                             size=blob.size,
                             hash_value=hash_value,
                             hash_type=hash_type,
                             meta={"type": "gcr",
                                   "src": blob.url,
                                   "proxy": True},  # Docker contents are always proxied
                             storage_name=storage_name)

    def exists(self, path=None):
        # todo: interface with docker api to check if the image exists locally
        return False

    @classmethod
    def compute_hash(cls, src: str):
        image_data: dict = cloud_utils.get_gcr_image_data(src)
        if not image_data:
            raise exceptions.InvalidObjectSourceError(msg=f"invalid source: {src} not found")
        return image_data.get("hash_type"), image_data.get("hash_value")

    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
    async def download(self, store, aio_client, timeout, callback=None):
        """download from remote to asset store"""
        # todo: wire with docker api
        if callback:
            callback()

    @property
    def can_download(self):
        return False

    @property
    def can_upload(self):
        return False

    @property
    def remote_url(self):
        return self.meta.get("src")

    @property
    def staging_url(self):
        return None

    @property
    def cache_path(self):
        return None

    def add_ref(self, **kwargs):
        # todo: determine how to do ref counting for docker images
        pass

    def remove_ref(self, **kwargs):
        pass

    def clear_from_cache(self, **kwargs):
        pass
