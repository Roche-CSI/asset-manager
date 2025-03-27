import os
from typing import Callable

from asset_pluggy.storage.urls.storage_url import StorageURL, PATH_SEPARATOR


class PosixURL(StorageURL):
    # TODO: mane the host uniform with BlobStoreURL
    host = "file://"

    def __init__(self, url: str, ignore: str = None, callback: Callable = None):
        super().__init__(
            url=os.path.realpath(url) + PATH_SEPARATOR if url.endswith(PATH_SEPARATOR) else os.path.realpath(url),
            ignore=ignore,
            callback=callback)

    def parse_url(self, url: str) -> None:
        self.dir_name = os.path.dirname(url)

    def is_valid(self):
        return os.path.exists(self.url)

    def url_for_blob(self, host: str, name: str):
        # sanitize the name by removing leading/trailing slashes
        return f"{host}{name.strip(PATH_SEPARATOR)}"

    def is_remote(self):
        # always False for Posix paths
        return False
