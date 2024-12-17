import abc
import os
from typing import Callable
from asset_utils.utils import ch_dir
from asset_manager.plugins import register_plugins


class AssetStoreDebug(abc.ABC):
    """
    app wrapper for triggering from IDE run configuration
    """
    target_dir = None

    def __init__(self, target_dir=None):
        self.target_dir = target_dir

    def run(self, callable: Callable):
        register_plugins()
        if self.target_dir and not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir, exist_ok=True)

        if self.target_dir:
            with ch_dir(self.target_dir):
                callable()
        else:
            callable()
