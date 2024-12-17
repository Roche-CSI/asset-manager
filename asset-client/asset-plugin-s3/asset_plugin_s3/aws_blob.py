from typing import Any

from asset_pluggy.storage import BlobData
from asset_pluggy.storage import BlobStoreURL
from asset_utils.common.exceptions import AssetException
from asset_utils.utils.file_utils import FileUtils


class AwsBlob(BlobData):
    """Class to handle AWS S3 blob data."""
    _aws_obj = None
    _multipart_size = None

    def initialize(self, data: Any, url_object: BlobStoreURL):
        """Initializes the AwsBlob object with data from an S3 object or S3 object summary.

        Parameters
        ----------
        data : Any
            A dict or s3.ObjectSummary or s3.object.
        url_object : BlobStoreURL
            The URL of the blob.
        """
        self._aws_obj = data
        try:
            if type(self._aws_obj) is dict:  # json data from S3Proxy
                self._initialize_from_dict(data=self._aws_obj)
                return
            elif hasattr(self._aws_obj, 'content_type'):  # s3.Object
                self._initialize_from_s3_object(s3_obj=self._aws_obj)
            else:
                self._initialize_from_s3_summary_object(s3_summary_obj=self._aws_obj)
        except Exception as e:
            raise AssetException(f"Error initializing blob from {url_object.url}") from e
        self.host = url_object.host
        self.url = url_object.url_for_blob(host=self.host, bucket=self.bucket, name=self.name)

    def _initialize_from_s3_object(self, s3_obj: Any):
        """Initializes the AwsBlob object with data from an S3 object.

        Parameters
        ----------
        s3_obj : Any
            The S3.object.
        """
        self.bucket = s3_obj.bucket_name
        self.name = s3_obj.key
        self.size = s3_obj.content_length
        # s3 mostly returns content-type as binary/octet-stream so we try to guess it
        # self.content_type = FileUtils.mime_type(self.name) or s3_obj.content_type
        # aws returns files + directory unlike gs which returns only files
        # self.is_file = bool(self.content_type != 'application/x-directory')
        # check all possible checksums, the structure here is different thant s3.ObjectSummary
        # note: aws_blob returns inconsistent check_sum_algorithm keys, sometimes the keys are present
        # if the value is null - so we add an extra protection to ensure hash can not be null
        if hasattr(s3_obj, "checksum_crc32") and getattr(s3_obj, "checksum_crc32"):
            self.hashes["crc32"] = getattr(s3_obj, "checksum_crc32")
        if hasattr(s3_obj, "checksum_crc32_c") and getattr(s3_obj, "checksum_crc32_c"):
            self.hashes["crc32_c"] = getattr(s3_obj, "checksum_crc32_c")
        if hasattr(s3_obj, "checksum_sha1") and getattr(s3_obj, "checksum_sha1"):
            self.hashes["sha1"] = getattr(s3_obj, "checksum_sha1")
        if hasattr(s3_obj, "checksum_sha256") and getattr(s3_obj, "checksum_sha256"):
            self.hashes["sha256"] = getattr(s3_obj, "checksum_sha256")

        self.hashes["etag"] = s3_obj.e_tag
        if '-' in s3_obj.e_tag and self._parse_etag(s3_obj.e_tag)[1] == '1':
            # if number of parts is 1, then self.size is the multipart size
            self._multipart_size = self.size

    def _initialize_from_s3_summary_object(self, s3_summary_obj: Any):
        """Initializes the AwsBlob object with data from an S3 object summary.

        Parameters
        ----------
        s3_summary_obj : Any
            The s3.ObjectSummary.
        """
        self.bucket = s3_summary_obj.bucket_name
        self.name = s3_summary_obj.key
        self.size = s3_summary_obj.size
        # if hasattr(s3_summary_obj, "checksum_algorithm"):
        #     # todo: verify whats the checksum value when this attribute is present in the object.
        #     hash_type = getattr(s3_summary_obj, "checksum_algorithm") or "md5"
        # e-tag has extra quotes, so we strip quotes
        # etag has 2 parts separated by "-", first part is the md5,
        # second part is the number of parts in which the file was uploaded
        self.hashes["etag"] = s3_summary_obj.e_tag
        if '-' in s3_summary_obj.e_tag and self._parse_etag(s3_summary_obj.e_tag)[1] == '1':
            # if number of parts is 1, then self.size is the multipart size
            self._multipart_size = self.size

    def _initialize_from_dict(self, data: dict):
        """Initialize the AwsBlob object from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the blob data.
        """
        self.bucket = data.get("bucket")
        self.hashes = data.get("hashes")
        self.host = data.get("host")
        self.name = data.get("name")
        self.path_in_asset = data.get("path_in_asset")
        self.size = data.get("size")
        self.url = data.get("url")

    @property
    def content_type(self):
        """Get the content type of the blob.

        Refactored into a property to avoid extra network calls involved in getting the content-type of s3

        Returns the content type of the blob. If the blob is an S3 object, it returns the content type of
        the S3 object. If the blob is an S3 object summary, it returns the MIME type of the blob based on
        its name or the content type of the S3 object summary.

        Returns
        -------
        str
            The content type of the blob.
        """
        if hasattr(self._aws_obj, 'content_type'):  # s3.Object
            return getattr(self._aws_obj, 'content_type')
        else:
            # note: this is refactored into a separate property for better list-blobs performance,
            # self._parse_content_type(obj=s3_summary_obj)
            # makes this slower by 0.6 seconds per call, so if you are checking 500 objects,
            # it would take about 4 minutes which is painfully slow
            return FileUtils.mime_type(self.name) or self._parse_content_type(obj=self._aws_obj)

    @property
    def is_file(self):
        """Check if the blob is a file.

        Refactored into property because of content_type refactoring above.

        Returns
        -------
        bool
            True if the blob is a file, False otherwise.

        Notes
        -----
        aws returns files + directory unlike gs which returns only files.
        """
        # self.is_file = bool(self.content_type != 'application/x-directory')
        return bool(self.content_type != 'application/x-directory')

    @property
    def multipart_size(self) -> int:
        """Get the part size of the multipart upload.

        Returns
        -------
        int
            The part size of the multipart upload.

        Raises
        ------
        AssetException
            If the blob is a multipart upload but the multipart_size is not initialized.
        """
        if self.is_multipart and not self._multipart_size:
            raise AssetException("Multipart size is not initialized. Please set the multipart size.")
        return self._multipart_size

    @multipart_size.setter
    def multipart_size(self, size: int):
        """Set the part size of the multipart upload.

        Parameters
        ----------
        size : int
            The part size of the multipart upload.
        """
        self._multipart_size = size

    @property
    def is_multipart(self) -> bool:
        """Check if the blob is a multipart upload.

        Returns True if the ETag of the blob indicates a multipart upload, False otherwise.

        Returns
        -------
        bool
            True if the blob is a multipart upload, False otherwise.
        """
        return bool('-' in self.hashes.get("etag", ""))

    def _parse_etag(self, etag: str) -> list:
        """Parse the ETag of the blob if it is multipart.

        Parameters
        ----------
        etag : str
            The ETag of the blob.

        Returns
        -------
        list
            A list containing the ETag and the number of parts in the upload.
        """
        # remove extra quotes
        return etag[1:-1].split("-")

    def _parse_content_type(self, obj: Any):
        """Get the content-type of an S3 object summary.

        Parameters
        ----------
        obj : Any
            The S3 object summary.

        Returns
        -------
        str
            The content-type of the S3 object summary.
        """
        try:
            return obj.get()['ContentType']
        except Exception as e:
            self.log.info(str(e))
            return None

    def compute_hash(self) -> tuple:
        raise NotImplementedError

    def get_hash_preferences(self) -> list:
        return [*super().get_hash_preferences(), "etag"]
