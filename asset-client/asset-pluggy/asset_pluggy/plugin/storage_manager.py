from typing import Dict, Type

from asset_pluggy.plugin.plugin_manager import PluginManager
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_utils.common.exceptions import AssetException
from asset_utils.common.singleton import Singleton


class AssetStorageConflictException(AssetException):
    def __init__(self, prefix: str, storage, prev_storage):
        msg = f'Input type `{prefix}` provided by {storage.__name__} already registered by {prev_storage.__name__}'
        super().__init__(self, msg)


class StorageManager(Singleton):
    _storage_providers: Dict[str, Type[AssetStorage]]

    def post_init(self, **kwargs):
        self._storage_providers = {}
        self._init_providers()

    def _init_providers(self):
        storage_providers = PluginManager.shared().hook.asset_storage_get()

        for storage in storage_providers:
            for prefix in storage.prefixes:
                prev_storage = self._storage_providers.get(prefix, None)
                if prev_storage:
                    raise AssetStorageConflictException(prefix=prefix, storage=storage, prev_storage=prev_storage)
                else:
                    self._storage_providers[prefix] = storage

    def get_storage(self, prefix: str, name: str = None):
        if prefix:
            return self._storage_providers.get(prefix, None)
        if name:
            for storage in self._storage_providers.values():
                if storage.name == name:
                    return storage
            return None

    def get_providers(self):
        return self._storage_providers
