import os

from asset_utils.utils import utils
from .storage_url import StorageURL, PATH_SEPARATOR

HOST_SEPARATOR = "://"


class BlobStoreURL(StorageURL):
    host: str = None
    bucket: str = None
    path: str = None  # path to search for in bucket
    dir_name: str = None  # we need the dir_name to calculate the relative path for objects
    pattern: str = None  # for selecting a subset of files

    def parse_url(self, url: str) -> None:
        """parses a blob's url into:
        - storage i.e. gs, s3 or azure etc
        - bucket_name
        - blob_name

        Parameters
        ----------
        url: str
            can also include glob patterns

        Returns
        -------
        None

        """
        if not url:
            return

        if HOST_SEPARATOR not in url:
            self.log.info(f"not found: {url} doesn't contain {HOST_SEPARATOR}")
            return
        self.host, blob_url = url.split(HOST_SEPARATOR)
        if not blob_url:
            return
        idx = blob_url.find(PATH_SEPARATOR)
        if idx == -1:
            self.bucket = blob_url  # last part is the bucket
            return
        if idx > 0:
            self.bucket = blob_url[0:idx]
        if idx < len(blob_url) - 1:
            self.path = blob_url[idx + 1:]
        # check if there is pattern
        if self.path:
            pattern = utils.find_pattern(self.path)
            if pattern:
                # prefix is the parent directory
                prefix = self.path[:len(self.path) - len(pattern)]
                self.pattern = prefix + pattern  # need the full path string for fnmatch to work
                self.path = prefix

            dir_name = os.path.dirname(self.path)
            # sanitize by remove any leading or trailing slashes
            if dir_name:
                self.dir_name = dir_name.strip(PATH_SEPARATOR)

    def is_valid(self):
        return bool(self.host and self.bucket)  # path is optional for listing

    def is_remote(self):
        return self.is_valid()

    def url_for_blob(self, host: str, bucket: str, name: str):
        """construct the url for a blob object"""
        # sanitize the name by removing leading/trailing slashes
        return f"{host}{HOST_SEPARATOR}{bucket}{PATH_SEPARATOR}{name.strip(PATH_SEPARATOR)}"
