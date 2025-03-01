from __future__ import annotations
from .content import Content, StorageSystems


class FileContent(Content):

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
    def storage_system_id(cls):
        return StorageSystems.GCS

