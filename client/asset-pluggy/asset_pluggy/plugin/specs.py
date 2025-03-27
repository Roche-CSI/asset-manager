from typing import Type

from asset_pluggy.plugin import hook_spec
from asset_pluggy.plugin.asset_object import AssetObject
from asset_pluggy.storage.asset_storage import AssetStorage


class StoragePlugin:
    """Storage plugin interface which can be used to discover registered storage backends    """

    @hook_spec
    def asset_storage_get(self) -> Type[AssetStorage]:
        """provides a storage backend to be used for storing asset data
        :return: AssetStorage compatible subclass
        """
        pass


class ObjectPlugin:
    @hook_spec
    def asset_object_get(self) -> Type[AssetObject]:
        """provides a Object type for any custom handling of data being added to asset"""
        pass


class PreCommitPlugin:
    """pre-commit rules for asset"""

    @hook_spec
    def asset_pre_commit_get(self) -> None:
        raise NotImplementedError


class ValidationPlugin:
    """asset validation rules"""

    @hook_spec
    def asset_validators_get(self) -> None:
        raise NotImplementedError


__all__ = [StoragePlugin, ObjectPlugin]
