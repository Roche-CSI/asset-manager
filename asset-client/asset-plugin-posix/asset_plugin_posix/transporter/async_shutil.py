import asyncio
import os
import shutil

from asset_pluggy.storage.transporter import TransportResource
from asset_utils.utils.log_utils import get_logger

logger = get_logger(__name__)


def copy_resources(resources: [TransportResource], credentials: dict = None):
    # TODO: switch to async after creating conda package for aioshutil
    # return asyncio.run(__async_copy_resources(credentials=credentials, resources=resources))
    for resource in resources:
        os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
        shutil.copy2(resource.src, resource.dst)


async def __async_copy_resources(resources: [TransportResource], credentials: dict):
    """copies files from src to dst

    Parameters
    ----------
    resources: list of TransportResource
        list of resources to be copied
    credentials: dict
        credentials to access files

    Returns
    -------
    list
        resources that were copied
    """
    result = []
    await asyncio.gather(*[__async_copy_resource(resource=resource,
                                                 result=result
                                                 ) for resource in resources])
    return result


async def __async_copy_resource(resource: TransportResource, result: list):
    os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
    # TODO: activate after creating conda package for aioshutil
    # res = await aioshutil.copy2(resource.src, resource.dst)
    # result.append(res)
    # resource.on_transfer_complete(res)
