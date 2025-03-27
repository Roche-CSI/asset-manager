import os

from cached_property import cached_property

from asset_pluggy.storage import BlobStoreURL
from asset_pluggy.storage.transporter import TransportResource
from asset_utils.common import exceptions
from asset_utils.utils import aws_hash
from asset_utils.utils.file_utils import FileUtils

DEFAULT_MULTIPART_SIZE = 8 * 1024 * 1024  # 8MB


class AwsTransportResource(TransportResource):
    @classmethod
    def from_transport_resource(cls, res: TransportResource):
        return cls(src=res.src, dst=res.dst, callback=res.callback)


class AwsUploadResource(AwsTransportResource):
    @cached_property
    def dst_url(self) -> BlobStoreURL:
        return BlobStoreURL(url=self.dst)


class AwsDownloadResource(AwsTransportResource):
    @cached_property
    def src_url(self) -> BlobStoreURL:
        return BlobStoreURL(url=self.src)

    def compute_dest_hash(self, hash_type: str) -> tuple:
        """Computes the destination hash.

        If the `hash_type` is 'etag', the destination hash is computed using the ETag of the source object.
        Also, the hash value becomes a list of ETags for possible multipart sizes.

        Parameters
        ----------
        hash_type : str
            The type of the hash.

        Returns
        -------
        tuple
            The hash type and the hash value of the `dst` file.
        """
        if hash_type == "etag":
            return aws_hash.file_etags(filepath=self.dst, etag=self.src_hash[1])
        else:
            return super().compute_dest_hash(hash_type=hash_type)

    def verify_checksum(self) -> bool:
        """Verifies the checksum after download.

        if the src_hash_type is etag, then we need to verify the etag differently.

        Returns
        -------
        bool
            True if the checksum is verified, False otherwise.
        """
        if not self.src_hash:
            return False
        src_hash_type, src_hash_val = self.src_hash
        # if the src_hash_type is etag, then we need to verify the etag differently
        if src_hash_type == "etag":
            return aws_hash.compare_etags(src_etag=self.src_hash, dst_etags=self.dst_hash)
        return super().verify_checksum()

    def on_transfer_complete(self, *args) -> None:
        """Handles the completion of the transfer.

        For the download operation, the destination hash is computed directly from the bytes before writing to file.
        If the source hash type is 'etag', the destination hash is computed differently.

        Parameters
        ----------
        *args
            Variable length argument list.
        """
        # first, make sure the file is downloaded
        if not os.path.exists(self.dst):
            raise exceptions.ResourceDownloadError(f"failed to downloaded: {self.src}")

        # then, compute the hash of the downloaded file
        if self.src_hash:
            src_hash_type, src_hash_val = self.src_hash
            if src_hash_type == "etag":
                self.dst_hash = aws_hash.bytes_etags(file_bytes=args[-1], etag=src_hash_val)
            else:
                self.dst_hash = FileUtils.bytes_hash(file_bytes=args[-1], hash_type=src_hash_type)
        super().on_transfer_complete(*args[:-1])


class AwsCopyResource(AwsTransportResource):
    def __init__(self,
                 src: str,
                 dst: str,
                 hash: tuple = None,
                 callback=None,
                 **kwargs):
        """Initializes an AwsCopyResource instance.

        Parameters
        ----------
        src : str
            The source URL.
        dst : str
            The destination URL.
        hash : tuple, optional
            The hash.
        callback : function, optional
            The callback function.
        **kwargs
            Arbitrary keyword arguments.

        Notes
        -----
        The `size` keyword argument is required for remote cloning. The `blob` keyword argument is used for remote copy.
        The `size` attribute must be initialized for copy operations.
        """
        super().__init__(src=src,
                         dst=dst,
                         hash=hash,
                         callback=callback)
        self.size = kwargs.get("size")
        if kwargs.get("blob"):  # asset cp command (remote copy)
            self.blob = kwargs.get("blob")
            self.size = self.blob.size
        if not self.size:
            raise exceptions.AssetException("Size is required for remote cloning.")

    @cached_property
    def src_url(self) -> BlobStoreURL:
        return BlobStoreURL(url=self.src)

    @cached_property
    def dst_url(self) -> BlobStoreURL:
        return BlobStoreURL(url=self.dst)

    @cached_property
    def multipart_size(self):
        """Returns the size of the multipart.

        If the blob attribute is not found, the default multipart size is returned.
        For single-part copy, the multipart size is None.
        asset clone --remote will not have blob, but will always use multipart copy

        Returns
        -------
        int
            The size of the multipart.
        """
        return self.blob.multipart_size if hasattr(self, "blob") else DEFAULT_MULTIPART_SIZE
