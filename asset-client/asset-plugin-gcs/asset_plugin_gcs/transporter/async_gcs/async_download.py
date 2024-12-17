import asyncio
import io
import json
import logging
import os

import aiohttp
import backoff

from asset_plugin_gcs.transporter.async_gcs.async_storage import AsyncStorage
from asset_plugin_gcs.transporter.gcs_transport_resource import GcsDownloadResource
from asset_utils.common import exceptions
from asset_utils.utils import UserLog
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.CRITICAL)

RETRIES = 5  # number of retries per file
GROUP_RETRIES = 5  # number of retries per group
MAX_RETRY_DELAY = 3600  # 1 hour for group retries
DEFAULT_DOWNLOAD_TIMEOUT = 3600  # 1 hour per file


def get_download_timeout() -> int:
    if os.getenv("ASSET_DOWNLOAD_TIMEOUT"):
        return int(os.getenv("ASSET_DOWNLOAD_TIMEOUT"))
    return DEFAULT_DOWNLOAD_TIMEOUT


def get_group_retries() -> int:
    if os.getenv("ASSET_DOWNLOAD_RETRIES"):
        return int(os.getenv("ASSET_DOWNLOAD_RETRIES"))
    return GROUP_RETRIES


def download_resources(credentials: dict, resources: [GcsDownloadResource]) -> list:
    """Downloads a list of files from a bucket with retries."""
    group_retries = get_group_retries()
    wait_generator = backoff.expo(base=4, factor=10)  # 10, 40, 160, 640, 2560...
    result = []

    # trying for the first time is not a retry attempt
    # that's why we use group_retries >= 0
    while group_retries >= 0 and resources:
        wait_seconds = next(wait_generator)
        if wait_seconds:
            if wait_seconds > MAX_RETRY_DELAY:
                # cap the wait time to MAX_RETRY_DELAY
                wait_seconds = MAX_RETRY_DELAY
                UserLog().alert(f"retry delay exceeded maximum limit of {MAX_RETRY_DELAY} seconds")
            # wait before retrying
            asyncio.run(asyncio.sleep(wait_seconds))

        success, failed_resources = asyncio.run(__async_download_resources(credentials=credentials,
                                                                           resources=resources))
        result.extend(success)
        resources = failed_resources
        group_retries -= 1

    return result


async def __async_download_resources(credentials: dict, resources: [GcsDownloadResource]):
    """Downloads a list of files from a bucket.

    Parameters
    ----------
    credentials : dict
        A dictionary containing the credentials to access the bucket.
    resources : [GcsDownloadResource]
        A list of GcsDownloadResource objects representing the files to be downloaded.

    Returns
    -------
    list
        A list of file paths that were downloaded.
    """
    # https://docs.aiohttp.org/en/stable/client_quickstart.html
    file_timeout = get_download_timeout()
    session_timeout = max(file_timeout * len(resources), file_timeout)
    timeout = aiohttp.ClientTimeout(total=session_timeout)
    # deactivate ssl verification, throws error in some macs otherwise
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                     timeout=timeout) as session:
        result = []
        async_client = AsyncStorage(session=session, service_file=io.StringIO(json.dumps(credentials)))
        tasks = [__async_download_resource(async_client=async_client,
                                           resource=resource,
                                           file_timeout=file_timeout,
                                           result=result
                                           ) for resource in resources]

        failed_resources = []
        # run all tasks concurrently and gather failed resources
        for task in asyncio.as_completed(tasks):
            try:
                await task
            # only catch BackoffRetryError and GroupRetryError
            # all other exceptions will be raised
            except exceptions.BackoffRetryError as e:
                failed_resources.append(e.data)
            except exceptions.GroupRetryError as e:
                failed_resources.append(e.data)

        return result, failed_resources


@backoff.on_exception(backoff.expo, exceptions.BackoffRetryError, max_tries=RETRIES, logger=logger)
async def __async_download_resource(async_client: AsyncStorage,
                                    resource: GcsDownloadResource,
                                    file_timeout: int,
                                    result: list) -> None:
    """Downloads a single file from a bucket.

    Will retry the download operation if exceptions.BackoffRetryError is raised.

    Parameters
    ----------
    async_client : AsyncStorage
        A client to interact with the storage service.
    resource : GcsDownloadResource
        An object representing the file to be downloaded.
    file_timeout : int
        The timeout duration for the file download operation.
    result : list
        A list to store the paths of the downloaded files.
    """
    os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
    try:
        await async_client.download_to_filename(
            bucket=resource.src_url.bucket,
            object_name=resource.src_url.path,
            filename=resource.dst,
            timeout=file_timeout,
            callback=lambda dst, data: resource.on_transfer_complete(dst, data)
        )
        result.append(resource.dst)
    # cast exceptions you want to retry into 2 types of asset exceptions
    # 1. aggregated retries: GroupRetryError - aggregate failures and retry in group
    # 2. immediate retries: BackoffRetryError - retry here on a single resource
    except asyncio.TimeoutError as e:  # backing off acquire_access_token
        raise exceptions.GroupRetryError(msg=f"{e}", data=resource) from e
    except aiohttp.ClientResponseError as e:
        if e.status == 429:  # Quota exceeded
            raise exceptions.GroupRetryError(msg=f"{e}", data=resource) from e
        if e.status == 403:  # Credentials error, no need to retry
            raise exceptions.InvalidStorageCredentialsError() from e
        raise exceptions.BackoffRetryError(msg=f"{e}", data=resource) from e
    except aiohttp.ClientError as e:
        raise exceptions.BackoffRetryError(msg=f"{e}", data=resource) from e
