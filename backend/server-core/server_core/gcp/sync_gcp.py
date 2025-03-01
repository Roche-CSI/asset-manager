from google.cloud import storage
import os
from typing import Union
import logging
from server_core.configs import Configs

logger = logging.getLogger(__name__)


def get_storage():
    return storage.Client.from_service_account_info(Configs.shared().storage_credentials)


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string[:]


def parse_gcp_url(url: str):
    """
    parses a gs:// url and returns bucket name and directory path
    :return:
    """
    if url.startswith("gs://"):
        url = remove_prefix(string=url, prefix="gs://")
    bucket_name = url.split("/")[0]
    object_path = remove_prefix(string=url, prefix=f"{bucket_name}/")
    return bucket_name, object_path


def list_url_blobs(gsurl, names_only=False) -> list:
    """lists blobs at a given gs url
    Parameters
    ----------
    gsurl: str
        gs://<path> url
    names_only: bool
        if True, return only blob_names else full blobs
    """
    bucket_name, prefix = parse_gcp_url(gsurl)
    return list_blobs(bucket_name, prefix, names_only)


def list_blobs(bucket, prefix=None, names_only=False) -> list:
    """
    returns a list of blobs
    :param bucket: str: cloud bucket name
    :param prefix: str: directory path
    :param names_only: pass True if you need just names
    :return: returns list[blob_name] if true else list[blob]
    """
    blobs = get_storage().list_blobs(bucket_or_name=bucket, prefix=prefix)
    return list(blobs) if not names_only else list(map(lambda x: x.name, blobs))


def get_blob_from_url(gs_url):
    """returns a blob object if it exists, None otherwise"""
    bucket_name, prefix = parse_gcp_url(gs_url)
    return get_blob_from_name(bucket_name=bucket_name, blob_name=prefix)


def get_blob_contents(blob) -> str:
    contents = blob.download_as_string()
    if type(contents) != str:
        contents = contents.decode("ascii")
    return contents


def get_blob_from_name(bucket_name, blob_name):
    client = get_storage()
    bucket = client.get_bucket(bucket_or_name=bucket_name)
    return bucket.get_blob(blob_name=blob_name)


def blob_exists(gs_url):
    """
    gs://url
    """
    bucket_name, prefix = parse_gcp_url(gs_url)
    storage_client = get_storage()
    bucket = storage_client.bucket(bucket_name)
    return storage.Blob(bucket=bucket, name=prefix).exists(storage_client)


def move_blob(src_url, dest_url):
    """Copies blob from a source url to dst url
    Parameters:
        src_url: gs://<bucket_name>/<blob_name>
        dest_url: src_url: gs://<bucket_name>/<blob_name>
    """
    # get bucket_name and blob_name from urls
    src_bucket_name, src_blob_name = parse_gcp_url(src_url)
    dst_bucket_name, dst_blob_name = parse_gcp_url(dest_url)
    # cloud blob api
    # https://cloud.google.com/storage/docs/copying-renaming-moving-objects#storage-move-object-python
    storage_client = get_storage()
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


def delete_blobs(bucket, blob_path):
    """
    Deletes blob
    :param bucket:
    :param blob_path: path excluding bucket name
    :return:
    """
    prefix = os.path.dirname(blob_path)
    blobs = list_blobs(bucket=bucket, prefix=prefix)

    for blob in blobs:
        if blob.name == blob_path:
            logger.info("deleting blob:{}".format(blob.name))
            blob.delete()
            return

    logger.warning("blob not found:{}".format(blob_path))


def update_cors_configuration(bucket_name, cors: dict):
    """Set a bucket's CORS policies configuration."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    bucket.cors = cors
    bucket.patch()
    print(f"Set CORS policies for bucket {bucket.name} is {bucket.cors}")
    return bucket