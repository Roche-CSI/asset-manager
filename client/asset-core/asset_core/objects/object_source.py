from typing import Callable

from asset_contents import Content
from asset_pluggy.storage import StorageData


class ObjectSource:
    blob: StorageData
    # path_in_asset, we need this to check for overrides
    # for example, user might enter 2 different urls and the query results could be such that
    # the path_in_asset of two objects collide. In that case, we consider only the first blob
    path_in_asset: str
    callback: Callable = None

    def __init__(self, blob: StorageData, path: str, callback=None):
        self.blob = blob
        self.path_in_asset = path
        self.callback = callback

    @property
    def content(self) -> Content:
        return self._content

    @content.setter
    def content(self, x):
        self._content = x

    def __eq__(self, other: StorageData):
        return self.path_in_asset == other.path_in_asset

    def __hash__(self):
        return hash(self.path_in_asset)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.path_in_asset)
