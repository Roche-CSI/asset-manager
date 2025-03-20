from typing import Any
from typing import Callable

from aiofiles import open as file_open
from gcloud.aio.storage import Storage

API_ROOT = 'https://www.googleapis.com/storage/v1/b'


class AsyncStorage(Storage):
    def __init__(self, *,
                 service_file=None,
                 token=None,
                 session=None) -> None:
        super().__init__(service_file=service_file, token=token, session=session)

    async def download_to_filename(self,
                                   bucket: str,
                                   object_name: str,
                                   filename: str,
                                   callback: Callable,
                                   **kwargs: Any) -> None:
        async with file_open(filename, mode='wb+') as file_object:
            # TODO: evaluate hash calculation during bytes streaming
            data = await self.download(bucket, object_name, **kwargs)
            if callback:
                callback(filename, data)
            await file_object.write(data)
