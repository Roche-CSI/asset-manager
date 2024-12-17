import asyncio
import logging
import os

import aiohttp
import backoff
import boto3
from yarl import URL

from asset_plugin_s3.transporter.aws_transport_resource import AwsDownloadResource
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import get_logger

RETRIES = 5  # number of retries in the event of failure
DEFAULT_DOWNLOAD_TIMEOUT = 3600  # 1 hr per file

logger = get_logger(__name__)
logger.setLevel(logging.CRITICAL)


# https://stackoverflow.com/questions/44915400/how-to-use-asyncio-to-download-files-on-s3-bucket

# TODO: add group retries similar to GCS
def download_resources(credentials: dict, resources: [AwsDownloadResource]):
    return asyncio.run(__async_download_resources(credentials=credentials, resources=resources))


def get_download_timeout() -> int:
    if os.getenv("ASSET_DOWNLOAD_TIMEOUT"):
        return int(os.getenv("ASSET_DOWNLOAD_TIMEOUT"))
    return DEFAULT_DOWNLOAD_TIMEOUT


async def __async_download_resources(credentials: dict, resources: [AwsDownloadResource]):
    file_timeout = get_download_timeout()
    session_timeout = max(file_timeout * len(resources), file_timeout)
    timeout = aiohttp.ClientTimeout(total=session_timeout)
    session = aiohttp.client.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                           timeout=timeout)
    s3_client = boto3.client('s3', **credentials)
    result = []
    await asyncio.gather(*[__async_download_resource(s3=s3_client,
                                                     session=session,
                                                     resource=resource,
                                                     result=result
                                                     ) for resource in resources])
    await session.close()
    return result


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES, logger=logger)
async def __async_download_resource(s3,
                                    session: aiohttp.client.ClientSession,
                                    resource: AwsDownloadResource,
                                    result: list
                                    ):
    request_url = s3.generate_presigned_url('get_object', {
        'Bucket': resource.src_url.bucket,
        'Key': resource.src_url.path
    })
    os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
    FileUtils.create_file_if_not_exists(path=resource.dst)

    async with session.get(URL(request_url, encoded=True)) as response:
        with open(resource.dst, 'wb') as file:
            # TODO: evaluate hash calculation during bytes streaming
            data = await response.read()
            file.write(data)
            result.append(resource.dst)
            resource.on_transfer_complete(resource.dst, data)
