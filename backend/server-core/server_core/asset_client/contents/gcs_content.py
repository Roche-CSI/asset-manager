from __future__ import annotations
from .content import Content, StorageSystems


class GcsContent(Content):
    """ Gcs File Object, files that are already in a gcp bucket and need not be uploaded again.
    """

    def __init__(self, **kwargs):
        super().__init__(**self.validate_kwargs(kwargs))

    @classmethod
    def storage_system_id(cls):
        return StorageSystems.GCS

    def serialize(self) -> dict:
        """serializes for storing in yaml"""
        return {field: getattr(self, field) for field in self.__class__.serialize_fields() if hasattr(self, field)}

    def can_download(self):
        return True

    @classmethod
    def compute_hash(cls, src=None) -> tuple:
        """
        Parameters
        ----------
        src: Blob
            gs Blob object

        Returns
        -------
        tuple of hash_value and hash_type
        """
        if not src:
            return None, None
        hv, ht = src.md5_hash, "md5"
        if not hv:
            # gcp doesn't support md5 for chunked upload files
            hv, ht = src.crc32c, "crc32c"
        return ht, hv

    # async def transfer_to_remote(self, aio_client, callback=None):
    #     stg_bucket, stg_prefix = parse_gcp_url(url=self.staging_url)
    #     repo_bucket, repo_prefix = parse_gcp_url(url=self.remote_url)
    #     # 1. copy from src bucket to dest bucket
    #     copy_res: dict = await aio_client.copy(bucket=stg_bucket,
    #                                            object_name=stg_prefix,
    #                                            destination_bucket=repo_bucket,
    #                                            new_name=repo_prefix,
    #                                            timeout=60)
    #
    #     if self.hash_value == copy_res.get("md5Hash"):
    #         self.log.info("finished copying:{}".format(copy_res))
    #         self.state = self.states.COMMITTED
    #     else:
    #         self.log.error("error in copying file".format(copy_res))
    #         return
    #
    #     # 2 delete
    #     delete_res = await aio_client.delete(bucket=stg_bucket,
    #                                          object_name=stg_prefix,
    #                                          timeout=60)
    #     self.log.info("deleted from staging:{}".format(delete_res))
    #     if callback:
    #         callback(copy_res)
