from __future__ import annotations

import os

from asset_pluggy.storage.blob import StorageData
from asset_utils.common import exceptions
from asset_utils.utils.file_utils import FileUtils
from .content import Content
from .content_stat import ContentStat


class PosixContent(Content):
    file_stat: ContentStat = None

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
               proxy: bool = False) -> PosixContent:
        # proxy contents are only allowed from remote sources
        if proxy:
            raise exceptions.UnSupportedOperation("proxy assets can only be created from remote sources")
        cls._validate_path(src=blob.name)
        hash_type, hash_val = blob.get_hash()
        return PosixContent(mime=blob.content_type,
                            size=blob.size,
                            meta={},
                            hash_value=hash_val,
                            hash_type=hash_type,
                            storage_name=storage_name)

    @classmethod
    def _validate_path(cls, src):
        """Validates path exists, raises exception

        Parameters
        ----------
        src: str
            dir or file path

        Returns
        -------
        """
        if not os.path.exists(os.path.abspath(src)):
            raise exceptions.InvalidObjectSourceError(msg=f"\nfile not found: {os.path.relpath(src, os.getcwd())}")

    @property
    def can_download(self):
        return True

    @property
    def can_upload(self):
        return True

    @classmethod
    def de_serialize(cls, asset, data: dict) -> PosixContent:
        return super(PosixContent, cls).de_serialize(asset, data)

    @classmethod
    def compute_hash(cls, src=None) -> tuple:
        """
        Parameters
        ----------
        src str
            absolute path of file

        Returns
        -------
        tuple of hash_type and hash_value
        """
        abs_path = os.path.abspath(src)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            return FileUtils.file_hash(abs_path)
        else:
            raise exceptions.InvalidObjectSourceError(f"file not found:{src}")
