import asyncio
import os

import aiofiles
import backoff

from asset_plugin_s3.mounted_bucket.mounted_resource import AwsMountedResource
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure


def copy_resources(resources: [AwsMountedResource]) -> list:
    """Function to copy resources."""
    return asyncio.run(__async_copy_resources(resources=resources))


async def __async_copy_resources(resources: [AwsMountedResource]) -> list:
    """Asynchronous function to copy resources."""
    result = []
    max_workers = 10
    semaphore = asyncio.Semaphore(max_workers)

    async def bounded_copy_and_verify(resource: AwsMountedResource):
        async with semaphore:
            return await __async_copy_resource(resource, result)

    bounded_tasks = [bounded_copy_and_verify(res) for res in resources]
    await asyncio.gather(*bounded_tasks)
    return result


@backoff.on_exception(backoff.expo, Exception, max_tries=RETRIES)
async def __async_copy_resource(resource: AwsMountedResource, result: list):
    """Asynchronous function to copy a single resource."""
    os.makedirs(os.path.dirname(resource.dst_url.posix_url), exist_ok=True)
    # copy the file
    async with (aiofiles.open(resource.src_url.posix_url, "rb") as srcf,
                aiofiles.open(resource.dst_url.posix_url, "wb") as dstf):
        while True:
            chunk = await srcf.read(4096)
            if not chunk:
                break
            await dstf.write(chunk)

    result.append(resource.dst)
    resource.on_transfer_complete(resource.dst)
