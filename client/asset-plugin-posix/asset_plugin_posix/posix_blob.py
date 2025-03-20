from asset_pluggy.storage import StorageData
from asset_plugin_posix.posix_url import PosixURL
from asset_utils.utils import aws_hash
from asset_utils.utils.file_utils import FileUtils


class PosixBlob(StorageData):
    name: str = None  # filepath
    content_type: str = None
    hashes: dict = None
    size: int = None

    def initialize(self, data: dict, url_object: PosixURL):
        self.name = data.get("name")
        self.content_type = data.get("content_type")
        self.size = data.get("size")
        self.host = url_object.host
        self.url = url_object.url_for_blob(host=self.host, name=self.name)

    def compute_hash(self) -> tuple:
        # assume that its local, this will throw error if it's an url
        # which the behaviour we want because we should have the hash-value in order to add an url
        hash_type, hash_value = FileUtils.file_hash(abs_path=self.name)
        return hash_type, hash_value

    def compare_hash(self, other: StorageData) -> bool:
        """
        Compares the current PosixBlob object with another StorageData object.

        This method calculates the hash of the current PosixBlob object based on the hash_type of the other
        StorageData object. If the other object's hash_type is "etag", it handles etags separately by calculating
        the etags of the file and comparing it with the other object's etag. Otherwise, it calculates the hash of
        the file based on the other object's hash_type and compares it with the other object's hash_value.

        Args:
            other (StorageData): The other StorageData object to compare with.

        Returns:
            bool: True if the hashes match, False otherwise.
        """
        other_hash_type, other_hash_value = other.get_hash()
        if other_hash_type == "etag":  # other blob is an AwsBlob
            if other.is_multipart:
                _, file_etag = aws_hash.file_etag(filepath=self.name, part_size=other.multipart_size)
            else:
                _, file_etag = aws_hash.file_etag(filepath=self.name)
            return file_etag == other_hash_value
        # calculate the hash of the file based on the other hash_type
        _, file_hash_value = FileUtils.file_hash(abs_path=self.name, hash_type=other_hash_type)
        return file_hash_value == other_hash_value
