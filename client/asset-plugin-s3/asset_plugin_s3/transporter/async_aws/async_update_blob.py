import asyncio

import aioboto3

from asset_plugin_s3.aws_blob import AwsBlob
from asset_utils.common import exceptions


def update_multipart_sizes(credentials: dict, blobs: [AwsBlob]):
    # filter out multipart blobs
    multipart_blobs = []
    for blob in blobs:
        try:
            blob.multipart_size
        except exceptions.AssetException:
            multipart_blobs.append(blob)
    return asyncio.run(_async_update_multipart_sizes(credentials=credentials, blobs=multipart_blobs))


async def _async_update_multipart_sizes(credentials: dict, blobs: [AwsBlob]):
    session = aioboto3.Session()
    async with session.client(service_name='s3', **credentials) as s3_client:
        updated_blobs = []
        await asyncio.gather(*[
            _async_update_multipart_size(client=s3_client,
                                         blob=blob,
                                         updated=updated_blobs,
                                         ) for blob in blobs])
        return updated_blobs


async def _async_update_multipart_size(client, blob: AwsBlob, updated: list):
    first_part = await client.head_object(Bucket=blob.bucket,
                                          Key=blob.name,
                                          PartNumber=1)
    blob.multipart_size = first_part['ContentLength']
    updated.append(blob)
