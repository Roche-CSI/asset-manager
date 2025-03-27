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

    def to_dict(self) -> dict:
        """Used in the server to serialize the object."""
        data = super().to_dict()
        data.update({
            "url": self.url,
            "host": self.host,
            "bucket": self.bucket,
            "name": self.name,
            "hashes": self.hashes,
            "size": self.size,
            "content_type": self.content_type,
            "is_file": self.is_file
        })
        return data
