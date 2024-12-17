from google.cloud import storage as gcs

from asset_pluggy.storage import BlobStoreURL
from asset_pluggy.storage import storage_utils
from asset_plugin_gcs.transporter.async_gcs import async_delete


class GcsStorageMixin:

    @property
    def gcs_client(self) -> gcs.Client:
        return gcs.Client.from_service_account_info(self.credentials)

    def fetch_blob_data(self, url: BlobStoreURL):
        return self.fetch_data_from_bucket(bucket_name=url.bucket,
                                           blob_name=url.path)

    def check_if_blob_exists(self, url: BlobStoreURL):
        # no blob path means the url is a bucket
        if not url.path:
            return False
        bucket = self.gcs_client.bucket(bucket_name=url.bucket)
        return bucket.blob(blob_name=url.path).exists()

    def fetch_data_from_bucket(self, bucket_name, blob_name):
        bucket = self.gcs_client.get_bucket(bucket_or_name=bucket_name)
        return bucket.get_blob(blob_name=blob_name)

    def fetch_blobs_list(self, url: BlobStoreURL):
        return self.fetch_blobs_list_from_bucket(bucket=url.bucket,
                                                 prefix=url.path,
                                                 pattern=url.pattern,
                                                 ignore=url.ignore)

    def fetch_blobs_list_from_bucket(self, bucket: str,
                                     prefix: str = None,
                                     pattern: str = None,
                                     ignore: str = None) -> list:
        """Fetches the list of blobs from the bucket.

        TODO: Use match_glob to filter the blobs based on the pattern.
        https://cloud.google.com/storage/docs/json_api/v1/objects/list#list-object-glob
        make sure pattern filter works same across AWS and GCS
        """
        # fetch blobs from the bucket filtered by prefix
        blobs = self.gcs_client.list_blobs(bucket_or_name=bucket, prefix=prefix)
        # filter blobs based on pattern and ignore
        return storage_utils.filter_blobs(blobs=blobs,
                                          name_key="name",
                                          pattern=pattern,
                                          ignore=ignore)

    def _delete_blob_urls(self, urls: [BlobStoreURL]):
        async_delete.delete_urls(credentials=self.credentials, urls=urls)
