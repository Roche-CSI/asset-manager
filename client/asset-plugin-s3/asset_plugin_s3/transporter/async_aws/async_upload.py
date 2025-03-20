import asyncio
import os

import aioboto3
import aiohttp
import backoff
from aiobotocore.config import AioConfig

from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure
DEFAULT_UPLOAD_TIMEOUT = 3600  # 1 hr per file


def upload_resources(credentials: dict, resources: [AwsUploadResource]):
    return asyncio.run(__async_upload_resources(credentials=credentials, resources=resources))


def get_upload_timeout() -> int:
    if os.getenv("ASSET_UPLOAD_TIMEOUT"):
        return int(os.getenv("ASSET_UPLOAD_TIMEOUT"))
    return DEFAULT_UPLOAD_TIMEOUT


async def __async_upload_resources(credentials: dict, resources: [AwsUploadResource]) -> list:
    file_timout = get_upload_timeout()
    session_timout = max(file_timout * len(resources), file_timout)
    session = aioboto3.Session()
    async with session.client(service_name='s3',
                              config=AioConfig(connect_timeout=session_timout),
                              aws_access_key_id=credentials.get("aws_access_key_id"),
                              aws_secret_access_key=credentials.get("aws_secret_access_key"),
                              region_name=credentials.get("region_name")) as s3_client:
        result = []
        await asyncio.gather(*[
            async_upload_resource(s3_client=s3_client,
                                  resource=resource,
                                  result=result
                                  ) for resource in resources])
        return result


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES)
async def async_upload_resource(s3_client,
                                resource: AwsUploadResource,
                                result: list):
    res = await s3_client.upload_file(Filename=resource.src,
                                      Bucket=resource.dst_url.bucket,
                                      Key=resource.dst_url.path)
    result.append(res)
    resource.on_transfer_complete(res)
