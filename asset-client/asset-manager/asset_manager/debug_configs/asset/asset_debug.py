import abc
import os
from typing import Callable
from asset_utils.utils import ch_dir
from asset_manager.plugins import register_plugins


class AssetDebug(abc.ABC):
    """
    app wrapper for triggering from IDE run configuration
    """
    asset_location = None

    def __init__(self, asset_name: str = None, debug_dir: str = None, asset_location: str = None):
        self.asset_location = asset_location or os.path.join(debug_dir or self.get_debug_dir(), asset_name)

    def get_debug_dir(self):
        """create a debug_data folder inside your asset-manager directory"""
        if not hasattr(self, "_debug_dir"):
            levels = 3
            dir_name = os.path.dirname(__file__)
            for i in range(0, levels):
                dir_name = os.path.dirname(dir_name)
            self._debug_dir = os.path.join(dir_name, "debug_data")
        return self._debug_dir

    def run(self, callable: Callable):
        register_plugins()
        if not self.asset_location or not os.path.exists(self.asset_location):
            raise Exception(f"invalid asset-location: {self.asset_location}")

        with ch_dir(self.asset_location):
            callable()
