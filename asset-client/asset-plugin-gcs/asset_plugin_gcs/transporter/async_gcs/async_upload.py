import asyncio
import io
import json
import os

import aiohttp
import backoff

from asset_plugin_gcs.transporter.async_gcs.async_storage import AsyncStorage
from asset_plugin_gcs.transporter.gcs_transport_resource import GcsUploadResource
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure
DEFAULT_UPLOAD_TIMEOUT = 3600  # 1 hour per file


def get_upload_timeout() -> int:
    if os.getenv("ASSET_UPLOAD_TIMEOUT"):
        return int(os.getenv("ASSET_UPLOAD_TIMEOUT"))
    return DEFAULT_UPLOAD_TIMEOUT


def upload_resources(credentials: dict, resources: [GcsUploadResource]):
    return asyncio.run(__async_upload_resources(credentials=credentials, resources=resources))


async def __async_upload_resources(credentials: dict, resources: [GcsUploadResource]) -> list:
    """Uploads a list of files to a bucket.

    Parameters
    ----------
    credentials : dict
        A dictionary containing the credentials to access the bucket.
    resources : [GcsUploadResource]
        A list of GcsUploadResource objects representing the files to be uploaded.

    Returns
    -------
    list
        A list of results from the upload operations.
    """
    file_timeout = get_upload_timeout()
    session_timeout = max(file_timeout * len(resources), file_timeout)
    timeout = aiohttp.ClientTimeout(total=session_timeout)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                     timeout=timeout) as session:
        async_client = AsyncStorage(session=session,
                                    service_file=io.StringIO(json.dumps(credentials)))
        # deactivate ssl verification, throws error in some macs otherwise
        result = []
        await asyncio.gather(*[__async_upload_resource(async_client=async_client,
                                                       resource=resource,
                                                       file_timeout=file_timeout,
                                                       result=result
                                                       ) for resource in resources])
        return result


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES)
async def __async_upload_resource(async_client: AsyncStorage,
                                  resource: GcsUploadResource,
                                  file_timeout: int,
                                  result: list) -> None:
    """Uploads a single file to a bucket.

    Parameters
    ----------
    async_client : AsyncStorage
        A client used to interact with the storage service.
    resource : GcsUploadResource
        A GcsUploadResource object representing the file to be uploaded.
    file_timeout : int
        The timeout duration for the file upload operation.
    result : list
        A list to store the results of the upload operations.
    """
    res = await async_client.upload_from_filename(bucket=resource.dst_url.bucket,
                                                  object_name=resource.dst_url.path,
                                                  filename=resource.src,
                                                  timeout=file_timeout,
                                                  force_resumable_upload=True)
    result.append(res)
    resource.on_transfer_complete(res)
