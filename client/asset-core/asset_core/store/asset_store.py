from __future__ import annotations

import os

from cached_property import cached_property

from asset_core.configs import Configs, AppSettings
from asset_db import AssetsDB, StoreDB
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils import list_files
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin, LogColors

# this will eventually be the group_id / project_id
STORE_ID = '.be34edd1-844a-4f16-972f-b2a32a5bf63d'


class AssetStore(LoggingMixin):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call shared() instead')

    def __repr__(self):
        return self.home_dir

    @classmethod
    def shared(cls, create_if_not_exists=False) -> AssetStore:
        if not cls._instance:
            _instance = cls.__new__(cls)
            if not _instance.is_valid():
                if create_if_not_exists:
                    try:
                        store = cls.create_store()
                        cls.user_log.success("Success\n")
                        cls.user_log.info(f"created asset store at:{store.home_dir}")
                        return store
                    except exceptions.AssetStoreCreateError as e:
                        e.logs.add("in order to work, asset-manager needs a ASSET_HOME directory", LogColors.INFO)
                        e.logs.add(f"{UserCommands().set_asset_store()}")
                        raise
                else:
                    raise exceptions.AssetStoreInvalidError("invalid asset-store, missing store id")
            cls._instance = _instance
        return cls._instance

    @cached_property
    def hashlist_db(self) -> AssetsDB:
        return AssetsDB(path=self.hash_list_file)

    @property
    def db(self) -> StoreDB:
        return StoreDB(path=self.store_file)

    def storage_url(self, staging=False):
        bucket = AppSettings.shared().storage_url(staging=staging)
        if not bucket:
            raise exceptions.RemoteStorageError()
        return bucket

    def repo_meta_dir(self, repo_id):
        return os.path.join(self.store_dir, "repos", repo_id)

    def add_to_temp_assets(self, class_name, asset_data):
        self.db.add_temp_asset(class_name, asset_data)

    def remove_from_temp_assets(self, seq_id, class_name):
        self.db.remove_temp_asset(class_name=class_name, seq_id=seq_id)

    def list_temp_assets(self, class_name) -> dict:
        return self.db.list_temp_assets(class_name=class_name)

    def get_temp_asset_id(self, asset_name: str):
        class_name, seq_id = asset_name.split("/")
        assets = self.list_temp_assets(class_name)
        for asset_id in assets:
            if assets[asset_id] == seq_id:
                return asset_id
        return None

    def is_valid(self):
        return self.__class__.is_store_exists(self.store_dir)

    @classmethod
    def is_store_exists(cls, dir_path):
        """checks if the directory is a valid asset store
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return False
        store_dir = cls.get_store_dir(dir_path=dir_path)
        id_file = os.path.join(store_dir, cls._store_id())
        return os.path.exists(id_file) and os.path.isfile(id_file)

    def add_repo(self, repo_id, data):
        # registers a repo with the asset-store
        self.db.add_repo(repo_id=repo_id, data=data)

    def remove_repo(self, repo_id):
        self.db.remove_repo(repo_id)

    def repo_data(self, repo_id):
        return self.list_repos().get(repo_id, {})

    def list_repos(self):
        return self.db.get_repos()

    def prune_repos(self):
        """removes repos that are not valid"""
        prune_ids = []
        for repo_id, data in self.list_repos().items():
            if not self.__class__.is_valid_repo(repo_id=repo_id, path=data.get("path")):
                prune_ids.append(repo_id)
        if not prune_ids:
            return False
        for prune_id in prune_ids:
            self.remove_repo(repo_id=prune_id)
        return True

    @classmethod
    def is_valid_repo(cls, path, repo_id):
        id_file = cls.id_file(repo_root=path, repo_id=repo_id)
        return os.path.exists(id_file) and os.path.isfile(id_file)

    @classmethod
    def id_file(cls, repo_root, repo_id):
        return os.path.join(repo_root, Configs.shared().asset.asset_dir, f".{repo_id}.id")

    @classmethod
    def create_store(cls) -> AssetStore:
        """creates asset store and adds signature"""
        dst = cls.get_store_dir()
        cls.validate_store_dir(dst)
        os.makedirs(dst, exist_ok=True)
        id_file = os.path.join(dst, cls._store_id())
        FileUtils.create_file_if_not_exists(path=id_file)
        return AssetStore.shared()

    @classmethod
    def validate_store_dir(cls, dst):
        if os.path.exists(dst):
            # if it's a file we can't do anything, user needs to delete the file
            # or set ASSETS_HOME environment variable
            if os.path.isfile(dst):
                raise exceptions.AssetStoreCreateError(f"invalid asset store, {dst} is a file")

            # directory might exist but is created by the user before asset-manager
            existing = list_files(dst)
            if existing:
                raise exceptions.AssetStoreCreateError(f"{dst} already exists and is not empty")

    @property
    def home_dir(self):
        return AppSettings.shared().assets_home

    @property
    def store_dir(self):
        return self.__class__.get_store_dir(dir_path=self.home_dir)

    @classmethod
    def get_store_dir(cls, dir_path=None):
        """returns the directory for store store-id file"""
        dir_path = dir_path or AppSettings.shared().assets_home

        # check if .asset is missing, append if so
        parent, dst = os.path.split(dir_path)
        if dst == ".assets":
            return dir_path

        return Configs.shared().asset_home.asset_store_dir.format(asset_home=dir_path)

    @classmethod
    def _store_id(cls):
        return STORE_ID

    @property
    def store_identifier(self):
        """Returns a store identifier that tells if it's a valid asset store
        we tag the store to the user_id, to make sure asset access are user specific
        """
        return os.path.join(self.store_dir, self.__class__._store_id())

    @property
    def project_id(self):
        project_id = os.getenv("ASSET_PROJECT_ID")
        if not project_id:
            raise exceptions.NoActiveProjectError()
        return project_id

    @property
    def project_dir(self):
        return Configs.shared().asset_home.assets_dir.format(asset_home=self.home_dir,
                                                             project_id=self.project_id)

    @property
    def user_id(self):
        user = AppSettings.shared().user
        if not user:
            raise exceptions.InvalidCredentialError()
        return user.get("username")

    def contents_cache_dir(self, class_id: str):
        return Configs.shared().asset_home.contents_cache_dir.format(asset_home=self.home_dir,
                                                                     project_id=self.project_id,
                                                                     class_id=class_id)

    def contents_url(self, staging=False) -> str:
        return Configs.shared().remote.contents_url(staging).format(storage_url=self.storage_url(staging=staging))

    @property
    def asset_classes_dir(self):
        return Configs.shared().asset_home.asset_classes_cache_dir.format(asset_home=self.home_dir,
                                                                          project_id=self.project_id)

    @property
    def class_list_file(self):
        return Configs.shared().asset_home.class_list_file.format(asset_home=self.home_dir,
                                                                  project_id=self.project_id)

    @property
    def class_list_url(self):
        return os.path.join(self.asset_classes_url, Configs.shared().asset_home.class_list_file_name)

    @property
    def asset_classes_url(self):
        return Configs.shared().remote.asset_classes_url.format(storage_url=self.storage_url())

    def aliases_url(self, class_id):
        url = Configs.shared().remote.asset_aliases_url.format(storage_url=self.storage_url())
        return os.path.join(url, class_id)

    def asset_class_url(self, id):
        return os.path.join(self.asset_classes_url, f"{id}.yaml")

    def asset_class_file(self, id):
        return Configs.shared().asset_home.asset_class_file.format(asset_home=self.home_dir,
                                                                   project_id=self.project_id,
                                                                   class_id=id)

    @property
    def hash_list_file(self):
        return Configs.shared().asset_home.hash_list_file.format(asset_home=self.home_dir,
                                                                 project_id=self.project_id)

    @property
    def store_file(self):
        return os.path.join(self.store_dir, Configs.shared().asset_home.asset_store_file)

    @property
    def manifests_dir(self):
        return Configs.shared().asset_home.manifests_cache_dir.format(asset_home=self.home_dir,
                                                                      project_id=self.project_id)

    def cached_manifest_file(self, asset_id, ver_number):
        return os.path.join(self.manifests_dir, asset_id, f"{ver_number}.json")

    def content_stats_file(self, class_id: str):
        return Configs.shared().asset_home.content_stats_file.format(asset_home=self.home_dir,
                                                                     project_id=self.project_id,
                                                                     class_id=class_id)

    @property
    def asset_list_file_name(self):
        return Configs.shared().asset_home.asset_list_file_name

    @property
    def assets_url(self):
        return Configs.shared().remote.assets_url.format(storage_url=self.storage_url())

    def class_assets_url(self, class_id):
        return os.path.join(self.assets_url, class_id, '')

    def asset_url(self, class_id, seq_id):
        # add a trailing slash otherwise it messes up gcs lookup with prefix, since
        # gcs doesn't have any concept of directories.
        # for example rnn_model/1 returns all blobs
        # with prefix 1, instead we want to be looking only at blobs that are inside
        return os.path.join(self.class_assets_url(class_id), str(seq_id), '')

    def asset_file_url(self, class_id, seq_id):
        return os.path.join(self.asset_url(class_id, seq_id), self.asset_file_name)

    @property
    def asset_file_name(self):
        return Configs.shared().asset.asset_file_name

    @property
    def assets_cache_dir(self):
        return Configs.shared().asset_home.assets_cache_dir.format(asset_home=self.home_dir,
                                                                   project_id=self.project_id)

    def asset_cache(self, class_id, seq_id):
        return os.path.join(self.assets_cache_dir, class_id, str(seq_id))

    def asset_file(self, class_id, seq_id):
        return os.path.join(self.asset_cache(class_id, seq_id), self.asset_file_name)
