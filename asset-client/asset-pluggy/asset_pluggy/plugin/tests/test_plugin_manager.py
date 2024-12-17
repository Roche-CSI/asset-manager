from abc import ABC
from typing import Type

from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.plugin_manager import PluginManager
from asset_pluggy.plugin.specs import AssetStorage


def test_plugin_manager():
    class TestStorage(AssetStorage, ABC):
        prefix = "test-storage"

    class TestStoragePlugin:
        @hook_impl
        def asset_storage_get(self) -> Type[AssetStorage]:
            return TestStorage

    plm = PluginManager.shared()
    plm.register(TestStoragePlugin())
    storages = plm.hook.asset_storage_get()
    # checking singleton also
    plm2 = PluginManager.shared()
    assert plm2 == plm
    storages2 = plm2.hook.asset_storage_get()
    assert len(storages) == 1
    assert len(storages2) == 1
    for storge in storages:
        assert storge is TestStorage
        assert storge.prefix == "test-storage"

    for storge in storages2:
        assert storge is TestStorage
        assert storge.prefix == "test-storage"
