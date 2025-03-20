import os
from functools import cached_property
from typing import Union

import boto3
import botocore
from botocore.errorfactory import ClientError

from asset_pluggy.storage import StorageData, StorageURL, BlobStoreURL
from asset_pluggy.storage import storage_utils
from asset_plugin_s3.aws_auth import AwsAuth, get_aws_id_k_date
from asset_plugin_s3.aws_blob import AwsBlob
from asset_plugin_s3.transporter import AsyncAwsTransporter
from asset_utils.utils import utils


class AwsHttpHandler:
    """AWS Http Handler class for handling AWS S3 operations using boto3 http requests."""

    def __init__(self, credentials: dict = None):
        self.cred = credentials

    @cached_property
    def credentials(self) -> dict:
        """Fetches and returns AWS credentials.

        This method first checks if the AWS credentials are provided by the user. If not, it fetches the
        aws_access_key_id and k_date from the server. It also updates the auth type map to redirect to the
        custom AwsAuth class.

        Returns
        -------
        dict
            A dictionary containing AWS credentials.
        """
        cred = self.cred
        # cred = None  # for testing purposes
        # update the auth type map to redirect to the custom AwsAuth class
        botocore.auth.AUTH_TYPE_MAPS.update({"s3v4": AwsAuth})
        # if the aws_access_key_id and aws_secret_access_key are there it means the user has provided the credentials.
        # is not then we fetch the aws_access_key_id and k_date from the server
        if not cred or "aws_access_key_id" not in cred and "aws_secret_access_key" not in cred:
            server_creds = get_aws_id_k_date()  # TODO: fetch it from the server instead of using a test function
            cred = {} if cred is None else cred
            cred["aws_access_key_id"] = server_creds["aws_access_key_id"]
            cred["aws_secret_access_key"] = ""
            os.environ["ASSET_K_DATE"] = server_creds["k_date"]  # set the k_date in the environment variable
        return cred

    def allows_object_add(self):
        """Checks if object addition is allowed."""
        return True

    def allows_proxy(self):
        """Checks if proxy is allowed."""
        return True

    def get_transporter(self) -> AsyncAwsTransporter:
        """Returns an instance of AsyncAwsTransporter.

        The AsyncAwsTransporter is initialized with the AWS credentials.

        Returns
        -------
        Transporter
            An instance of AsyncAwsTransporter.
        """
        return AsyncAwsTransporter.shared(credentials=self.credentials)

    @property
    def s3_client(self):
        return boto3.client('s3', **self.credentials)

    @property
    def s3_resource(self):
        return boto3.resource('s3', **self.credentials)

    def get_storage_url(self, url_string: str, ignore: str = None) -> StorageURL:
        return BlobStoreURL(url=url_string, ignore=ignore)

    def get_blob(self, url_string: str) -> AwsBlob:
        """Get the blob instance from the given URL."""
        aws_url = BlobStoreURL(url=url_string)
        blob_data = self.fetch_blob_data(url=aws_url)
        return AwsBlob(data=blob_data, url_object=aws_url)

    def fetch_blob_data(self, url: BlobStoreURL):
        return self.fetch_data_from_bucket(bucket_name=url.bucket, blob_name=url.path)

    def fetch_data_from_bucket(self, bucket_name, blob_name):
        return self.s3_resource.Object(bucket_name, blob_name)

    def url_is_file(self, url: Union[StorageURL, str]) -> bool:
        """Checks if the URL is a file.

        Blobs are files, so if a blob exists then it's a file
        else either the url doesn't exist or it's a directory
        """
        if type(url) is str:
            url = BlobStoreURL(url=url)
        return self.check_if_blob_exists(url)

    def blob_exists(self, url_string: str) -> bool:
        """Checks if a blob exists at the given URL."""
        return self.check_if_blob_exists(url=BlobStoreURL(url=url_string))

    def check_if_blob_exists(self, url: BlobStoreURL) -> bool:
        # no blob path means the url is a bucket
        if not url.path:
            return False
        try:
            exists = self.s3_client.head_object(Bucket=url.bucket, Key=url.path)
            return bool(exists)
        except ClientError:
            return False

    def list_blobs(self, url: Union[str, StorageURL], ignore: str = None) -> [StorageData]:
        """Returns a list of AwsBlobs located at the url."""
        if type(url) is str:
            url = BlobStoreURL(url=url, ignore=ignore)
        blobs_list = self.fetch_blobs_list(url=url)
        return list(map(lambda x: AwsBlob(data=x, url_object=url), blobs_list))

    def fetch_blobs_list(self, url: BlobStoreURL):
        aws_bucket = self.s3_resource.Bucket(url.bucket)
        # fetch blobs from the bucket filtered by prefix
        blobs = list(aws_bucket.objects.filter(Prefix=url.path))
        # filter blobs based on pattern and ignore
        return storage_utils.filter_blobs(blobs=blobs,
                                          name_key="key",
                                          pattern=url.pattern,
                                          ignore=url.ignore)

    def delete_blobs(self, url_strings: [str]) -> None:
        """Deletes blobs at the given URLs."""
        self.delete_blob_urls(urls=list(map(lambda x: BlobStoreURL(url=x), url_strings)))

    def delete_blob_urls(self, urls: [BlobStoreURL]):
        # group by bucket
        groups = {}
        for url in urls:
            keys_list = groups.get(url.bucket, [])
            keys_list.append(url.path)
            groups[url.bucket] = keys_list
        # delete batch by batch
        for bucket in groups:
            self.batch_delete_s3(s3_client=self.s3_client, bucket=bucket, keys_list=groups.get(bucket))

    def batch_delete_s3(self, s3_client, bucket: str, keys_list: list):
        for batch in utils.batch(keys_list, batch_size=100):
            batch_to_delete = list(map(lambda x: {"Key": x}, batch))
            s3_client.delete_objects(Bucket=bucket, Delete={'Objects': batch_to_delete, 'Quiet': True})

    def filter_duplicate_blobs(self, src_blobs: [StorageData], dst_blobs: [StorageData]) -> (list, list):
        """Filters the source blobs to determine which blobs are new and which need to be replaced in the destination.

        If a blob in `src_blobs` has the same path_in_asset as a blob in `dst_blobs`, it compares their hashes.
        If the hashes are different, the blob is added to the replace_blobs list. If the path_in_asset is not
        found in `dst_blobs`, the blob is considered new and is added to the new_blobs list. For upload and download
        operations, the multipart sizes of the blobs are updated before hash comparison.

        Parameters
        ----------
        src_blobs : list
            A list of source blobs.
        dst_blobs : list
            A list of destination blobs.

        Returns
        -------
        tuple
            A tuple containing two lists: new_blobs and replace_blobs. new_blobs is a list of blobs that are new and
            replace_blobs is a list of blobs that need to be replaced in the destination.
        """
        # TODO: improve the overall implementation
        if not dst_blobs:  # nothing to filter against
            return src_blobs, []
        if all(isinstance(blob, AwsBlob) for blob in src_blobs) and all(
                isinstance(blob, AwsBlob) for blob in dst_blobs):  # asset cp remote copy
            new_blobs, replace_blobs = [], []
            # compare the path_in_asset and hash of the blobs
            dst_blob_map = {obj.path_in_asset: obj for obj in dst_blobs}
            for src_blob in src_blobs:
                if src_blob.path_in_asset in dst_blob_map:
                    # no need to update the multipart sizes before hash comparison
                    if not src_blob.compare_hash(dst_blob_map[src_blob.path_in_asset]):
                        replace_blobs.append(src_blob)
                else:
                    # new path_in_asset new object
                    new_blobs.append(src_blob)
            return new_blobs, replace_blobs

        # src_blobs or dst_blobs must be PosixBlob objects
        new_blobs, replace_blobs = [], []
        # compare the path_in_asset and hash of the blobs
        dst_blob_map = {obj.path_in_asset: obj for obj in dst_blobs}
        need_hash_compare = []
        for src_blob in src_blobs:
            if src_blob.path_in_asset in dst_blob_map:
                # need to compare hash
                need_hash_compare.append(src_blob)
            else:
                # new path_in_asset new object
                new_blobs.append(src_blob)

        if all(isinstance(blob, AwsBlob) for blob in need_hash_compare):  # asset cp download
            # update the multipart sizes of the blobs that need hash comparison
            self.get_transporter().update_multipart_blobs(blobs=need_hash_compare)
            for src_blob in need_hash_compare:
                posix_blob = dst_blob_map[src_blob.path_in_asset]
                if not posix_blob.compare_hash(src_blob):
                    replace_blobs.append(src_blob)
        else:  # asset cp upload
            # dst_blobs must be AwsBlob objects, update the multipart sizes
            self.get_transporter().update_multipart_blobs(
                blobs=[dst_blob_map[obj.path_in_asset] for obj in need_hash_compare])
            for posix_blob in need_hash_compare:
                dst_blob = dst_blob_map[posix_blob.path_in_asset]
                if not posix_blob.compare_hash(dst_blob):
                    replace_blobs.append(posix_blob)

        return new_blobs, replace_blobs
