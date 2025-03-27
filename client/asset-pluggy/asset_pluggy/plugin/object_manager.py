# No usage of ObjectManager found in the project.
from typing import Dict, Type

from asset_pluggy.plugin.asset_object import AssetObject
from asset_pluggy.plugin.plugin_manager import PluginManager
from asset_utils.common import exceptions, Singleton


class ObjectManager(Singleton):
    object_providers: Dict[str, Type[AssetObject]]

    def post_init(self):
        self.object_providers = {}
        self._init_providers()

    def _init_providers(self):
        plugin_manager = PluginManager()
        providers = plugin_manager.hook.asset_object_get()

        for provider in providers:
            prev_provider = self.object_providers.get(provider.unit, None)
            if prev_provider:
                raise exceptions.AssetObjectConflictException(provider, prev_provider)
            else:
                self.object_providers[provider.unit] = provider
