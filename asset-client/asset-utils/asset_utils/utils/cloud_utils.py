import logging
import socket
import subprocess

import requests
import speedtest

from asset_utils.common import exceptions
from asset_utils.utils import utils

logger = logging.getLogger(__name__)


def get_upload_speed():
    """returns upload speed in bytes, we use this to dynamically adjust the http request timeout"""
    return speedtest.Speedtest().upload() / 8.0  # speedtest output is bits


def get_download_speed():
    """returns the download speed in bytes"""
    return speedtest.Speedtest().download() / 8.0  # speedtest output is bits


def parse_gcp_url(url: str):
    """
    parses a gs:// url and returns bucket name and directory path
    :return:
    """
    if url.startswith("gs://"):
        url = utils.remove_prefix(string=url, prefix="gs://")
    bucket_name = url.split("/")[0]
    object_path = utils.remove_prefix(string=url, prefix=f"{bucket_name}/")
    return bucket_name, object_path


def is_gs_url(url: str):
    return url.startswith("gs://")


def is_s3_url(url: str):
    return url.startswith("s3://")


def is_gcr_url(url: str):
    return url and url.startswith("gcr.io/")


def internet_on(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def get_gcr_url(host_name, gcp_project: str, image: str):
    url = f"https://{host_name}/v2/{gcp_project}/{image}/tags/list"
    headers = {"Authorization": f"Bearer {get_gcloud_token()}"}
    res = requests.get(url=url, headers=headers)
    return res.json()


def get_gcloud_token():
    with subprocess.Popen(
            ["gcloud", "auth", "print-access-token"],
            stdout=subprocess.PIPE) as proc:
        result = proc.communicate()
        token = result[0].decode().strip()
        return token


def get_gcr_image_data(gcr_url: str):
    """parse gcr.io url

    Parameters
    ----------
    gcr_url

    Returns
    -------
    dict:
        {project, image, tag, sha}

    """
    # gcr_urls
    # 1. gcr.io/myproject/myimage@sha256:digest
    # 2. gcr.io/myproject/myimage:mytag1

    # check if its with a sha
    url_parts = gcr_url.split("@")
    if len(url_parts) == 2:
        # user passed url with sha256
        return parse_gcr_sha_url(image_url=url_parts[0], hash_url=url_parts[1])
    elif len(url_parts) == 1:
        return parse_gcr_tag_url(url_parts[0])
    else:
        return None


def parse_gcr_sha_url(image_url, hash_url):
    # 1. gcr.io/myproject/myimage@sha256:digest
    image_url_parts = image_url.split("/")
    project = image_url_parts[1]
    image = image_url_parts[2]

    # verify
    url_data: dict = get_gcr_url(host_name=image_url_parts[0], gcp_project=project, image=image)
    image_data = url_data.get("manifest")
    # this is a dict where keys are the hashes
    if not image_data:
        if is_permission_error(url_data):
            raise exceptions.InsufficientCredentialError(msg=f"permission denied to:{image_url}")
        else:
            raise exceptions.InvalidObjectSourceError(msg=f"{image_url} not found")

    for hash_name in image_data:
        if hash_name == hash_url:
            found = image_data.get(hash_name)
            found['hash_type'], found['hash_value'] = hash_name.split(":")
            found['name'] = url_data.get("name")
            return found

    return None


def parse_gcr_tag_url(gcr_url: str):
    # 2. gcr.io/myproject/myimage:mytag1
    image_url, tag = gcr_url.split(":")
    image_url_parts = image_url.split("/")
    project = image_url_parts[1]
    image = image_url_parts[2]
    # verify
    url_data: dict = get_gcr_url(host_name=image_url_parts[0], gcp_project=project, image=image)
    image_data = url_data.get("manifest")
    # this is a dict where keys are the hashes
    if not image_data:
        if is_permission_error(url_data):
            raise exceptions.InsufficientCredentialError(msg=f"permission denied to:{gcr_url}")
        else:
            raise exceptions.InvalidObjectSourceError(msg=f"{gcr_url} not found")
    for hash_name in image_data:
        data: dict = image_data.get(hash_name)
        if data and tag in data.get("tag"):
            data['hash_type'], data['hash_value'] = hash_name.split(":")
            data['name'] = url_data.get("name")
            return data


def is_permission_error(url_data: dict):
    errors = url_data.get("errors", [])
    for error in errors:
        if error.get("code") == "DENIED":
            return True
    return False
