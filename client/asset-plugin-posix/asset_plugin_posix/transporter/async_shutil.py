import os
import shutil

from asset_plugin_posix.transporter.posix_transport_resource import PosixTransportResource


def copy_resources(resources: [PosixTransportResource]):
    # return asyncio.run(__async_copy_resources(resources=resources))
    # TODO: switch to async after creating conda package for aioshutil
    for resource in resources:
        os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
        shutil.copy2(resource.src, resource.dst)

#
# async def __async_copy_resources(resources: [PosixTransportResource]):
#     result = []
#     await asyncio.gather(*[__async_copy_resource(resource=resource,
#                                                  result=result
#                                                  ) for resource in resources])
#     return result
#
#
# async def __async_copy_resource(resource: PosixTransportResource, result: list):
#     os.makedirs(os.path.dirname(resource.dst), exist_ok=True)
#     res = await aioshutil.copy2(resource.src, resource.dst)
#     result.append(res)
#     resource.on_transfer_complete(res)
