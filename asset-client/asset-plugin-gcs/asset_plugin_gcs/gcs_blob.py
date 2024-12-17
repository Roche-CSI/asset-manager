from google.cloud.storage.blob import Blob

from asset_pluggy.storage import BlobData
from asset_pluggy.storage.urls import BlobStoreURL


class GcsBlob(BlobData):

    def initialize(self, data: Blob, url_object: BlobStoreURL):
        self.bucket = data.bucket.name
        self.name = data.name
        self.content_type = data.content_type
        self.size = data.size
        self.is_file = True  # gs only returns files unlike s3 which returns files + directory
        if data.md5_hash:
            self.hashes["md5"] = data.md5_hash
        if data.crc32c:
            self.hashes["crc32c"] = data.crc32c
        self.host = url_object.host
        self.url = url_object.url_for_blob(host=self.host, bucket=self.bucket, name=self.name)

    def compute_hash(self) -> tuple:
        raise NotImplementedError
