import abc
from typing import Callable

from asset_utils.utils.log_utils import LoggingMixin

PATH_SEPARATOR = "/"


class StorageURL(LoggingMixin, metaclass=abc.ABCMeta):
    host: str = None
    url: str = None
    ignore: str = None
    # we need the dir_name to calculate the relative path for objects
    # every subclass must provide this value
    dir_name: str = None
    callback: Callable = None

    def __init__(self, url: str, ignore: str = None, callback: Callable = None):
        self.url = url
        self.ignore = ignore
        self.callback = callback
        self.parse_url(url=self.url)

    def execute_callback(self, *args):
        if self.callback:
            self.callback(*args)

    @abc.abstractmethod
    def parse_url(self, url: str) -> None:
        """parses a blob's url into:
        - storage i.e. gs, s3 or azure etc
        - bucket_name
        - blob_name

        Parameters
        ----------
        url: str

        Returns
        -------
        None

        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_valid(self):
        """verify if the url is sufficient to fetch data"""
        raise NotImplementedError

    @abc.abstractmethod
    def url_for_blob(self, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def is_remote(self):
        raise NotImplementedError
