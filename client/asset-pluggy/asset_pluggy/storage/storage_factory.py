import json
import os
from typing import Type

from asset_pluggy.plugin.storage_manager import StorageManager
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_pluggy.storage.mount_config import MountConfig
from asset_utils.common import exceptions


class StorageFactory:
    _instances = {}
    _storages = {}

    @classmethod
    def storage_with_prefix(cls, prefix: str) -> AssetStorage:
        storage = cls._storages.get(prefix, None)
        if not storage:
            storage = cls._add_storage(prefix=prefix)
        return storage

    @classmethod
    def _add_storage(cls, prefix: str):
        klass: Type[AssetStorage] = StorageManager.shared().get_storage(prefix=prefix)
        if not klass:
            raise exceptions.InvalidStorageBackendError(msg=f"{prefix} backend is not installed")
        storage = klass.shared()
        cls._storages[prefix] = storage
        return storage

    @classmethod
    def storage_for_url(cls, src_url: str):
        # translate to a standard blob url
        mt_cfg = cls.mount_config_for_url(src_url)
        if mt_cfg and mt_cfg.is_posix(src_url):
            # user might have passed posix
            norm_url = mt_cfg.posix_to_url(src_url)
        else:
            norm_url = src_url

        providers: dict = StorageManager.shared().get_providers()
        for prefix, storage_klass in providers.items():
            if norm_url.startswith(prefix):
                storage = cls.storage_with_prefix(prefix=prefix)
                if mt_cfg:
                    storage.mount_config = mt_cfg
                return storage
        return cls.default_storage()

    @classmethod
    def mount_configs(cls):
        cfgs = os.getenv("ASSET_BUCKET_MT_CONFIG")
        if cfgs:
            return [MountConfig(url=url, mount=mount) for url, mount in json.loads(cfgs).items()]
        return None

    @classmethod
    def mount_config_for_url(cls, src_url: str):
        mounts = cls.mount_configs()
        if mounts:
            for mount in mounts:
                # user can pass either posix or s3:// url
                if mount.is_posix(src_url) or mount.is_url(src_url):
                    return mount
        return None

    @classmethod
    def parse_sources(cls,
                      repo_dir: str,
                      targets: list,
                      proxy: bool = False,
                      dest_dir: str = None,
                      ignore: str = None) -> dict:
        """
        parses the targets which includes
         - collecting all files if the target is a directory
         - collecting all blobs/urls if the target is a gsurl or web url
        Parameters
        ----------
        repo_dir: str
            repo directory
        targets: [str]
            list of files, urls etc.
        proxy: bool
            if to be added as proxy
        dest_dir: str
            optional, to create a directory and add files in it
        ignore: str

        Returns
        -------
        dict:
            {storage_name: set<ContentSource>()}
        """
        result = {}
        for target in targets:
            storage: AssetStorage = cls.storage_for_url(src_url=target)
            if not storage.allows_object_add():
                raise exceptions.InvalidObjectSourceError(
                    f"you can not directly add objects from this source: {storage.name}")
            if proxy and not storage.allows_proxy():
                raise exceptions.InvalidObjectSourceError(f"proxy is not allowed for: {storage.name}")
            sources = storage.parse_blobs_from_url(repo_dir=repo_dir,
                                                   url_string=target,
                                                   ignore=ignore,
                                                   dest_dir=dest_dir)
            # fuse-mounted directories have an empty_file with trailing slash, we can't add these as assets
            sources = [item for item in sources if not str(item[0].name).endswith("/")]
            stored: dict = result.get(storage.name, {})
            for blob, path in sources:
                stored[path] = blob
            result[storage.name] = stored

        return result

    @classmethod
    def storage_with_name(cls, name: str):
        for storage_klass in cls._storages.values():
            if storage_klass.name == name:
                return storage_klass
        # check in storage factory
        klass: Type[AssetStorage] = StorageManager.shared().get_storage(prefix=None, name=name)
        if klass:
            return cls._add_storage(prefix=klass.prefixes[0])
        else:
            return cls.default_storage()

    @classmethod
    def default_storage(cls):
        return cls.storage_with_prefix(prefix=cls.default_storage_prefix())

    @classmethod
    def default_storage_prefix(cls) -> str:
        return "file://"  # Posix
