"""
This is the botocore upload that we need to test and unify with the existing async_upload
"""
import asyncio

import aiohttp
import backoff
from aiobotocore.session import get_session

# native
from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource
# plugins
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)
RETRIES = 5  # number of retries in the event of failure


def upload_resources(credentials: dict, resources: [AwsUploadResource]):
    return asyncio.run(__async_upload_resources(credentials=credentials, resources=resources))


async def __async_upload_resources(credentials: dict, resources: [AwsUploadResource]):
    """uploads a list of files to bucket

    Parameters
    ----------
    credentials: dict
        aws access credentials
    resources: [GcsUploadResource]

    Returns
    -------

    """
    session = get_session()
    async with session.create_client('s3',
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
    with open(resource.src, 'rb') as file:
        resp = await s3_client.put_object(Bucket=resource.dst_url.bucket,
                                          Key=resource.dst_url.path,
                                          Body=file)
        result.append(resp)
        resource.on_transfer_complete(resp)
