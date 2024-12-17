from abc import ABC

from .storage_data import StorageData


class BlobData(StorageData, ABC):
    url: str = None
    host: str = None
    bucket: str = None
    name: str = None
    hashes: dict = None  # hash_type is key, hash_value is value
    size: int = None
    content_type: str = None
    is_file: bool = None
