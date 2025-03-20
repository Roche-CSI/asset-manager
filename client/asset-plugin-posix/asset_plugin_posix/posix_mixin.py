import os

from asset_plugin_posix.posix_url import PosixURL
from asset_utils.common import exceptions
from asset_utils.utils import utils
from asset_utils.utils.file_utils import FileUtils

MUST_IGNORE = "*.asset*"


class PosixStorageMixin:

    def fetch_blob_data(self, url: PosixURL) -> dict:
        if not os.path.isfile(url.url):
            raise exceptions.InvalidStorageURLError(f"file not found: {url.url}")
        return self.get_file_data(path=url.url)

    def fetch_blobs_list(self, url: PosixURL) -> list:
        ignore = f"{MUST_IGNORE}"
        if url.ignore:
            ignore += f",{url.ignore}"

        files = utils.files_at_location(src=url.url, ignore=ignore)
        return [self.get_file_data(path=file) for file in files]

    def get_file_data(self, path: str):
        return {
            "name": path,
            "content_type": FileUtils.mime_type(src=path),
            "size": os.path.getsize(path)  # get size
        }

    def check_if_blob_exists(self, url: PosixURL) -> bool:
        return os.path.exists(url.url)

    def _delete_blob_urls(self, urls: [PosixURL]):
        for url in urls:
            if os.path.exists(url.url):
                os.remove(url.url)
                url.on_transfer_complete()
