from __future__ import annotations

import os

from asset_pluggy.storage.blob import StorageData
from asset_utils.common import exceptions
from asset_utils.utils.file_utils import FileUtils
from .posix_content import Content


class BlobStoreContent(Content):

    @classmethod
    def compute_hash(cls, src: str):
        abs_path = os.path.abspath(src)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            return FileUtils.file_hash(abs_path)
        else:
            raise exceptions.InvalidObjectSourceError(f"file not found:{src}")

    def __init__(self, **kwargs):
        super().__init__(**self.validate_kwargs(kwargs))

    @classmethod
    def create(cls, storage_name: str,
               blob: StorageData,
               proxy: bool = False) -> BlobStoreContent:
        """Create a new BlobStoreContent object from a StorageData object"""
        hash_type, hash_val = blob.get_hash()
        return BlobStoreContent(mime=blob.content_type,
                                size=blob.size,
                                hash_value=hash_val,
                                hash_type=hash_type,
                                meta={"type": storage_name,
                                      "src": blob.url,
                                      "proxy": proxy},
                                storage_name=storage_name)

    @property
    def source_url(self):
        return self.meta.get("src")

    @property
    def can_download(self):
        return True
        # return not self.is_proxy

    @property
    def can_upload(self):
        return False

    @classmethod
    def de_serialize(cls, asset, data: dict) -> BlobStoreContent:
        return super(BlobStoreContent, cls).de_serialize(asset, data)
