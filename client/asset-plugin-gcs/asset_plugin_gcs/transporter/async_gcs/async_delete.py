import asyncio
import io
import json

import aiohttp
import backoff

from asset_pluggy.storage import BlobStoreURL
from asset_plugin_gcs.transporter.async_gcs.async_storage import AsyncStorage
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure
DELETE_TIMEOUT = 60  # 10 minutes


def delete_urls(credentials: dict, urls: [BlobStoreURL]):
    return asyncio.run(__async_delete_urls(credentials=credentials, urls=urls))


async def __async_delete_urls(credentials: dict, urls: [BlobStoreURL]):
    """deletes a list of files from bucket

    Parameters
    ----------
    urls: [BlobStoreURL]

    Returns
    -------

    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async_client = AsyncStorage(session=session,
                                    service_file=io.StringIO(json.dumps(credentials)))
        # deactivate ssl verification, throws error in some macs otherwise
        result = []
        await asyncio.gather(*[__async_delete_url(async_client=async_client,
                                                  url=url,
                                                  result=result
                                                  ) for url in urls])
        return result


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES)
async def __async_delete_url(async_client: AsyncStorage,
                             url: BlobStoreURL,
                             result: list):
    delete_res = await async_client.delete(bucket=url.bucket,
                                           object_name=url.path,
                                           timeout=DELETE_TIMEOUT)
    result.append(delete_res)
    url.execute_callback(delete_res)
