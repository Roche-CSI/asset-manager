import json
import os
import shutil
import aiohttp
from gcloud.aio.storage import Storage as aioStorage
import aiofiles
import asyncio
import logging
import backoff
from server_core.asset_client.asset_object import AssetObject
from server_core.configs import Configs
from server_core.gcp import parse_gcp_url
from server_core.utils.file_utils import FileUtils
import tempfile
import io
from datetime import timedelta

logger = logging.getLogger(__name__)


def get_aio_token(credentials_server):
    result = asyncio.run(__get_token(credentials_server))
    return result


async def __get_token(credentials_server):
    async with aiohttp.ClientSession() as session:
        storage = aioStorage(session=session,
                             service_file=io.StringIO(json.dumps(credentials_server)))
        token = await storage.token.get()
        expiry = storage.token.access_token_acquired_at + timedelta(seconds=storage.token.access_token_duration)
        return {
            "access_token": token,
            "acquired_at": storage.token.access_token_acquired_at.timestamp(),
            "expires_at": expiry.timestamp()
        }


def move_from_staging(objects):
    """Uploads list of assets to cloud bucket and does a checksum validation
    """
    asyncio.run(_move_objects(objects))


async def _move_objects(objects: [AssetObject]):
    """Uploads a list of files to bucket
    Parameters:
        objects: list of AssetObject
    """
    # disable ssl verification, throws errors on some Macs otherwise
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async_client = aioStorage(session=session,
                                  service_file=io.StringIO(json.dumps(Configs.shared().storage_credentials))
                                  )
        await asyncio.gather(*[
            _async_move_asset(async_client=async_client,
                              asset_obj=obj,
                              ) for obj in objects
        ])
        logger.info("completed upload")


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
async def _async_move_asset(async_client, asset_obj: AssetObject):
    stg_bucket, stg_prefix = parse_gcp_url(url=asset_obj.staging_url)
    repo_bucket, repo_prefix = parse_gcp_url(url=asset_obj.remote_url)
    # 1. copy from src bucket to dest bucket
    copy_res = await async_client.copy(bucket=stg_bucket,
                                       object_name=stg_prefix,
                                       destination_bucket=repo_bucket,
                                       new_name=repo_prefix,
                                       timeout=60)
    logger.info("finished copying:{}".format(copy_res))
    # 2 delete
    delete_res = await async_client.delete(bucket=stg_bucket,
                                           object_name=stg_prefix,
                                           timeout=60
                                           )
    logger.info("deleted from staging:{}".format(delete_res))


def write_yaml_to_bucket(contents):
    """Writes data in yaml format to bucket
    contents: list
        list of dicts {"data": dict, "url": str}
    """

    temp_dir = tempfile.mkdtemp()

    for item in contents:
        file_name = os.path.basename(item["url"])
        path = os.path.join(temp_dir, file_name)
        FileUtils.write_yaml(path, item["data"])
        item["path"] = path

    asyncio.run(_async_write_yaml_to_bucket(contents))

    # # cleanup
    # for item in contents:
    #     if os.path.exists(item["path"]):
    #         os.remove(item["path"])
    shutil.rmtree(temp_dir)


async def _async_write_yaml_to_bucket(contents):
    """
    Uploads file to cloud bucket
    Parameters:
        data:
        list of dicts (data: {}, blob_name: {})
    """
    # deactivate ssl verification, throws error in some macs otherwise
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async_client = aioStorage(session=session,
                                  service_file=io.StringIO(json.dumps(Configs.shared().storage_credentials)))
        await asyncio.gather(*[
            _async_write_yaml_data(async_client=async_client,
                                   src=item["path"],
                                   dst=item["url"],
                                   ) for item in contents
        ])
        logger.info("completed upload")


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
async def _async_write_yaml_data(async_client, src, dst):
    async with aiofiles.open(src, mode="rb") as f:
        contents = await f.read()
        bucket, blob_name = parse_gcp_url(url=dst)
        res = await async_client.upload(bucket,
                                        blob_name,
                                        contents,
                                        timeout=60,
                                        force_resumable_upload=True)
