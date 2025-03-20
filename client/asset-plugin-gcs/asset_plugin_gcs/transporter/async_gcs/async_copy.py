import asyncio
import io
import json

import aiohttp
import backoff

from asset_plugin_gcs.transporter.async_gcs.async_storage import AsyncStorage
from asset_plugin_gcs.transporter.gcs_transport_resource import GcsCopyResource
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure
COPY_TIMEOUT = 600  # 10 minutes


def copy_resources(credentials: dict, resources: [GcsCopyResource]) -> list:
    return asyncio.run(__async_copy_resources(credentials=credentials, resources=resources))


async def __async_copy_resources(credentials: dict, resources: [GcsCopyResource]) -> list:
    """Copies a list of files to a bucket.

    Parameters
    ----------
    credentials : dict
        A dictionary containing the credentials to access the bucket.
    resources : [GcsCopyResource]
        A list of GcsCopyResource objects representing the files to be copied.

    Returns
    -------
    list
        A list of results from the copy operations.
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async_client = AsyncStorage(session=session,
                                    service_file=io.StringIO(json.dumps(credentials)))
        # deactivate ssl verification, throws error in some macs otherwise
        result = []
        await asyncio.gather(*[__async_copy_resource(async_client=async_client,
                                                     resource=resource,
                                                     result=result
                                                     ) for resource in resources])
        return result


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES)
async def __async_copy_resource(async_client: AsyncStorage,
                                resource: GcsCopyResource,
                                result: list) -> None:
    """Copies a single file to a bucket.

    Parameters
    ----------
    async_client : AsyncStorage
        A cient used to interact with the storage service.
    resource : GcsCopyResource
        A GcsCopyResource object representing the file to be copied.
    result : list
        A list to store the results of the copy operations.
    """
    res = await async_client.copy(bucket=resource.src_url.bucket,
                                  object_name=resource.src_url.path,
                                  destination_bucket=resource.dst_url.bucket,
                                  new_name=resource.dst_url.path,
                                  timeout=COPY_TIMEOUT)
    result.append(res)
    resource.on_transfer_complete(res)
