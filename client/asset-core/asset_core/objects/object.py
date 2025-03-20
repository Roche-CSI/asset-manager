from __future__ import annotations

import os
from typing import Callable

from asset_utils.common import exceptions
from asset_utils.utils.file_utils import FileUtils
from .asset_object import AssetObject


class Object(AssetObject):
    object_type = None

    def add_to_asset(self, asset, **kwargs):
        self.asset = asset
        self.asset.objects.add(self)
        self.content = self.asset.contents.add_content(content=self.content)
        self.content.add_to_asset(asset=asset, object=self)
        self.set_state(self.__class__.states.PENDING)

    def link_to_store(self, save: bool = False):
        """
        - calculate object stat

        Parameters
        ----------
        save

        Returns
        -------

        """
        # create stat
        self.update_object_stat(save=save)

    def link_from_store(self,
                        linking_type: str = "copy",
                        callback: Callable = None,
                        save: bool = False) -> bool:
        # todo: refactor to handle non-download contents such as docker
        #  most likely we need something other than content.exists()

        if not self.content.exists():
            raise exceptions.ContentNotAvailableError(f"unable to link content: {self.linked_path}")

        if self._transfer_from_store(linking_type=linking_type):
            self.update_object_stat(save=save)
        if callback:
            callback(self)

        return True

    def _transfer_from_store(self,
                             linking_type: str = "copy",
                             force: bool = True) -> bool:
        if not os.path.exists(self.content.cache_path):
            return False
        os.makedirs(os.path.dirname(self.linked_path), exist_ok=True)
        if os.path.exists(self.linked_path) and force:
            os.remove(self.linked_path)

        # link the file according to the linking type
        if linking_type == "copy":
            FileUtils.copy_file(src=self.content.cache_path, dst=self.linked_path)
        elif linking_type == "hardlink":
            FileUtils.hard_link_file(src=self.content.cache_path, dst=self.linked_path)
        elif linking_type == "symlink":
            FileUtils.sym_link_file(src=self.content.cache_path, dst=self.linked_path)
        else:
            raise exceptions.AssetException(f"Invalid linking type: {linking_type}")
        return True
