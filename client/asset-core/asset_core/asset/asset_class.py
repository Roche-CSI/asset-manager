from __future__ import annotations

import os

from asset_core.plugins import FileUtils, LoggingMixin, list_files, exceptions
from asset_core.store.asset_store import AssetStore
from asset_utils.common.user_commands import UserCommands
from .serializable import Serializable
from .status_enums import StatusEnums


class AssetClass(LoggingMixin, Serializable):
    id: str = None
    name: str = None
    asset = None
    project = None
    owner = None
    status: int = None

    def __init__(self,
                 id=None,
                 name=None,
                 store=None,
                 project=None,
                 owner=None):
        self.auto_save = False
        self.name = name
        self.store = store or AssetStore.shared()
        self.project = project
        self.id = id
        self.owner = owner
        self.status = StatusEnums.default()
        self.auto_save = True

    @classmethod
    def get_asset_class(cls, store, name) -> AssetClass:
        class_data = AssetClass.cached_class_data(store=store, name=name)
        asset_class = AssetClass(name=name, store=store)
        asset_class.de_serialize(asset=None, data=class_data)
        return asset_class

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if self.auto_save and self.asset:
            if key in self.__class__.serialize_fields():
                self.asset.db.update(**{"asset_class": self.serialize()})

    def de_serialize(self, asset, data: dict):
        self.asset = asset
        if not data:
            return None
        self.auto_save = False
        for key in self.__class__.serialize_fields():
            if key in data:
                setattr(self, key, data.get(key))
        self.auto_save = True

    def serialize(self) -> dict:
        return {key: getattr(self, key) for key in self.__class__.serialize_fields()}

    @classmethod
    def serialize_fields(cls):
        return ["id", "name", "project", "owner", "status"]

    """Functionalities for assets-fetching"""

    @property
    def cache_dir(self):
        if not self.id:
            return None
        return os.path.join(self.store.assets_cache_dir, self.id)

    @property
    def asset_list_file(self):
        if not self.cache_dir:
            return None
        return os.path.join(self.cache_dir, self.store.asset_list_file_name)

    @property
    def content_cache_dir(self):
        # todo: fix this and change to class_id
        #  we need to restrict the asset-class creation flow for this.
        #  asset-class must already be there before the content can be created
        cache_dir = self.store.contents_cache_dir(class_id=self.name)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    @property
    def content_stats_file(self):
        # todo: change to id, see above
        return self.store.content_stats_file(class_id=self.name)

    @property
    def remote_url(self):
        if not self.id:
            raise exceptions.AssetException("asset class-id not set")
        return self.store.asset_class_url(id=self.id)

    def list_assets(self) -> dict:
        # todo: refactor all class operations and remove dependency on name - switch to ids instead
        if not self.id:
            return {}
        assets = {}
        if os.path.exists(self.asset_list_file):
            assets: dict = FileUtils.read_yaml(self.asset_list_file)
        assets.update(self.store.list_temp_assets(class_name=self.name) or {})
        return assets

    @classmethod
    def list_classes(cls, store) -> dict:
        classes_dir = store.asset_classes_dir
        cls.logger().info("class-dir:{}".format(classes_dir))
        if not os.path.exists(classes_dir):
            return {}
        class_files = FileUtils.read_yamls_multi(cls.all_class_files(store=store))
        result = {}
        for obj in class_files.values():
            result[obj.get("id")] = obj
        return result

    @classmethod
    def all_class_files(cls, store: AssetStore):
        classes_dir = store.asset_classes_dir
        if not os.path.exists(classes_dir):
            return []
        files = list_files(classes_dir)
        # filter out non-active classes, user may have stale classes which have already been
        # deleted in remote

        # switch name and id
        active_classes = {y: x for x, y in cls.active_classes(store=store).items()}
        result = []
        for file in files:
            dir_name, file_name = os.path.split(file)
            file_name, extension = os.path.splitext(file_name)
            if file_name in active_classes:
                result.append(file)
        return result

    @classmethod
    def active_classes(cls, store) -> dict:
        if os.path.exists(store.class_list_file):
            return FileUtils.read_yaml(store.class_list_file)
        return {}

    @classmethod
    def get_id(cls, store, name):
        if not os.path.exists(store.class_list_file):
            raise exceptions.ClassListNotFoundError()
        class_list_data = FileUtils.read_yaml(store.class_list_file) or {}
        return class_list_data.get(name)

    @classmethod
    def cached_class_data(cls, store, name=None, id=None):
        if not id and not name:
            raise exceptions.AssetException("class-name or class-id not provided")

        id = id or cls.get_id(store, name)
        if not id:
            raise exceptions.AssetClassNotFoundError()
        try:
            return FileUtils.read_yaml(store.asset_class_file(id))
        except FileNotFoundError as e:
            asset_err = exceptions.AssetException(f"asset class file not found for class: {name}, id: {id}")
            asset_err.logs.add(UserCommands().fetch_classes())
            raise asset_err from e
        except Exception as e:
            raise exceptions.AssetClassNotFoundError(f"error reading asset class: {name}, id: {id}") from e

    @classmethod
    def class_list_url(cls, repo):
        return repo.store.class_list_url

    @classmethod
    def classes_cache(cls, repo):
        return repo.store.class_list_file
