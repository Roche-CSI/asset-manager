# No usage of gcs_utils.py found in this project
import logging
import os
from typing import Union

from google.cloud import storage

from asset_utils.utils import cloud_utils

logger = logging.getLogger(__name__)


def move_blob(src_url, dest_url):
    """Copies blob from a source url to dst url
    Parameters:
        src_url: gs://<bucket_name>/<blob_name>
        dest_url: src_url: gs://<bucket_name>/<blob_name>
    """
    # get bucket_name and blob_name from urls
    src_bucket_name, src_blob_name = cloud_utils.parse_gcp_url(src_url)
    dst_bucket_name, dst_blob_name = cloud_utils.parse_gcp_url(dest_url)
    # cloud blob api
    # https://cloud.google.com/storage/docs/copying-renaming-moving-objects#storage-move-object-python
    storage_client = storage.Client()
    src_bucket = storage_client.bucket(src_bucket_name)
    src_blob = src_bucket.get_blob(blob_name=src_blob_name)
    dst_bucket = storage_client.bucket(dst_bucket_name) if dst_bucket_name != src_bucket_name else src_bucket
    dst_blob = src_bucket.copy_blob(src_blob, dst_bucket, dst_blob_name)
    src_blob.delete()
    logger.info("Blob {} moved to blob {} in bucket {}.".format(
        src_blob_name,
        dst_blob.name,
        dst_bucket_name))


def get_blob_name(blob: Union[storage.Blob, str]):
    """
    Gets blob name (last part of the path).
    :param blob: instance of :class:`google.cloud.storage.Blob`.
    :return: name string.
    """
    if isinstance(blob, storage.Blob):
        return os.path.basename(blob.name)
    assert isinstance(blob, str)
    if blob.endswith("/"):
        blob = blob[:-1]
    return os.path.basename(blob)


def get_bucket(bucket_name):
    bucket = storage.Client().get_bucket(bucket_name)
    if not bucket:
        raise Exception("bucket not found:{}".format(bucket_name))
    return bucket


def add_cors_for_url(bucket_name, *urls):
    """
    Sets the CORS policy of a bucket
    Parameters
    ----------
    bucket_name
    urls

    Returns
    -------

    """
    bucket = get_bucket(bucket_name)
    cors = bucket.cors[0] if len(bucket.cors) > 0 else {}
    if not cors:
        cors = {
            "origin": [],
            "method": ["GET"],
            "responseHeader": ["Content-Type"],
            "maxAgeSeconds": 3600
        }
    for url in urls:
        if url not in cors["origin"]:
            cors["origin"].append(url)

    bucket.cors = [cors]
    bucket.patch()
    logger.info("Set CORS policies for bucket {} is {}".format(bucket.name, bucket.cors))
    return bucket


def removed_cors_for_url(bucket_name, *urls):
    bucket = get_bucket(bucket_name)
    cors = bucket.cors[0] if len(bucket.cors) > 0 else {}
    if not cors:
        return

    cors["origin"] = [x for x in cors["origin"] if x not in urls]
    bucket.cors = [cors]
    bucket.patch()
    logger.info("Set CORS policies for bucket {} is {}".format(bucket.name, bucket.cors))
    return bucket
