from abc import ABC
from typing import Type

from asset_pluggy.plugin import hook_impl
from asset_pluggy.plugin.plugin_manager import PluginManager
from asset_pluggy.plugin.specs import AssetStorage
from asset_pluggy.plugin.storage_manager import StorageManager


def test_storage_manager():
    class AwsStorageTest(AssetStorage, ABC):
        prefixes = ["s3-test"]

    class GcsStorageTest(AssetStorage, ABC):
        prefixes = ["gs-test"]

    class GcrStorageTest(AssetStorage, ABC):
        prefixes = ["gcr.io-test", "us.gcr.io-test"]

    class AwsStorageTestPlugin:
        @hook_impl
        def asset_storage_get(self) -> Type[AssetStorage]:
            return AwsStorageTest

    class GcsStorageTestPlugin:
        @hook_impl
        def asset_storage_get(self) -> Type[AssetStorage]:
            return GcsStorageTest

    class GcrStorageTestPlugin:
        @hook_impl
        def asset_storage_get(self) -> Type[AssetStorage]:
            return GcrStorageTest

    plm = PluginManager.shared()
    plm.register(AwsStorageTestPlugin())
    plm.register(GcsStorageTestPlugin())
    plm.register(GcrStorageTestPlugin())
    sm = StorageManager.shared()
    providers: dict = sm.get_providers()
    assert len(providers) == 4
    expected = {
        "s3-test": AwsStorageTest,
        "gs-test": GcsStorageTest,
        "gcr.io-test": GcrStorageTest,
        "us.gcr.io-test": GcrStorageTest
    }
    for key in expected:
        actual = providers[key]
        exp = expected[key]
        assert actual == exp
        for prefix in exp.prefixes:
            assert prefix in actual.prefixes
