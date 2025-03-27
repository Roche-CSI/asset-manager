"""
This is the botocore download that we need to test and unify with the existing async_download
"""
import asyncio
import os

import aiohttp
import backoff
from aiobotocore.session import get_session

# native
from asset_plugin_s3.transporter.aws_transport_resource import AwsDownloadResource
from asset_utils.utils.file_utils import FileUtils
# plugins
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure


def download_resources(credentials: dict, resources: [AwsDownloadResource]):
    return asyncio.run(__async_download_resources(credentials=credentials, resources=resources))


async def __async_download_resources(credentials: dict, resources: [AwsDownloadResource]) -> list:
    """Downloads a list of files from bucket

    Parameters
    ----------
    resources: [GcsDownloadResource]

    Returns
    -------
    list:
        list of filepaths downloaded

    """
    session = get_session()
    async with session.create_client('s3',
                                     aws_access_key_id=credentials.get("aws_access_key_id"),
                                     aws_secret_access_key=credentials.get("aws_secret_access_key"),
                                     region_name=credentials.get("region_name")) as s3_client:
        result = []
        await asyncio.gather(*[__async_download_resource(s3_client=s3_client,
                                                         resource=resource,
                                                         result=result
                                                         ) for resource in resources])
        return result


def get_s3_bj(client, s3_bucket, s3_key):
    """send request and retrieve the obj from S3"""
    resp = client.get_object(
        Bucket=s3_bucket,
        Key=s3_key
    )
    obj = resp['Body'].read()
    return obj


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=RETRIES)
async def __async_download_resource(s3_client, resource: AwsDownloadResource, result: list):
    # https://gist.github.com/mattwang44/0c2e0e244b9e5f901f3881d5f1e85d3a#file-downloadfroms3_async-py
    response = await s3_client.get_object(Bucket=resource.src_url.bucket, Key=resource.src_url.path)
    os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
    FileUtils.create_file_if_not_exists(path=resource.dst)
    with open(resource.dst, 'wb') as file:
        # TODO: evaluate hash calculation during bytes streaming
        data = await response["Body"].read()
        file.write(data)
        result.append(resource.dst)
        resource.on_transfer_complete(resource.dst, data)
