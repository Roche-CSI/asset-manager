from __future__ import annotations

import os
import shutil
from functools import cached_property
from typing import TYPE_CHECKING

from asset_core.api.repo_api import AssetAPI
from asset_core.api.store_api.clone_asset import CloneAssetAPI
from asset_core.api.store_api.copy import CopyAPI
from asset_core.api.store_api.fetch import FetchAPI
from asset_core.api.store_api.find import FindAPI
from asset_core.asset.asset_handle import AssetHandle
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.configs import configs
from asset_core.store import Repo, AssetStore
from asset_manager.app import ACTIVE_CONFIG_MODE
from asset_manager.plugins import register_plugins
from asset_manager.python_api.file import File
from asset_utils.common import exceptions
from asset_utils.utils import ch_dir

if TYPE_CHECKING:
    from asset_manager import ArtifactInputs

# make sure config mode is set properly
configs.Configs.shared(mode=ACTIVE_CONFIG_MODE)


class Artifact:
    path: str = None  # repo location
    _repo: Repo = None

    def __new__(cls, *args, **kwargs):
        register_plugins()
        return super().__new__(cls)

    def __init__(self, path: str):
        self.path = path
        if not self.path:
            # root can not be null here, unlike command line where we auto find the root if its missing
            raise exceptions.AssetException("required param missing or None: path")
        self._repo = Repo(self.path)

    @cached_property
    def _api(self):
        return AssetAPI(repo=self._repo)

    @property
    def _caches(self) -> list:
        """Cached properties to be cleared when the asset is updated or modified.

        Returns
        -------
        list
            The list of cached properties
        """
        return ["files", "history", "info", "status", "versions"]

    def _clear_cache(self, cache_name: str = None):
        # resets cached properties
        caches = [cache_name] if cache_name else self._caches
        for cache in caches:
            if cache in self.__dict__:  # check if the cache exists
                del self.__dict__[cache]

    @cached_property
    def files(self) -> dict:
        objects = self.info.get("objects")
        if not objects:
            return {}

        return {obj["path"]: File(**obj) for obj in objects}

    @cached_property
    def history(self) -> dict:
        api = self._api.version
        with api.environment():
            return api.list_version_history(jsonize=True)

    @cached_property
    def info(self) -> dict:
        api = self._api.info
        with api.environment():
            return api.asset_info(jsonize=True)

    @cached_property
    def status(self) -> dict:
        api = self._api.status
        with api.environment():
            return api.display_status(jsonize=True)

    @cached_property
    def versions(self) -> dict:
        api = self._api.version
        with api.environment():
            return api.list_versions_summary(jsonize=True)

    @property
    def active_version(self) -> str:
        """Returns the active version of the asset."""
        return self.info.get("asset").get("version")

    @property
    def metadata(self) -> dict:
        """Returns the metadata of the asset."""
        return self.info.get("asset").get("metadata")

    @property
    def attributes(self) -> dict:
        """Returns the attributes of the asset."""
        return self.info.get("asset").get("attributes")

    @property
    def tags(self) -> list:
        """Returns the tags of the asset."""
        return self.info.get("asset").get("tags")

    @property
    def class_name(self) -> str:
        """Returns the class name of the asset."""
        return self._repo.current_asset.get("asset_class").get("name")

    @property
    def asset_name(self) -> str:
        """Returns <class_name>/<seq_id> of the asset."""
        return self.info.get("asset").get("asset")

    @property
    def asset_version_name(self):
        """Returns the asset name with the active version.

        Returns
        -------
        str
            <class_name>/<seq_id>/<version> or None if the asset is temporary.
        """
        if self.is_temp:
            return None
        return f"{self.asset_name}/{self.active_version}"

    @property
    def title(self) -> str:
        """Returns the title of the asset."""
        return self.info.get("asset").get("title")

    @property
    def description(self) -> str:
        """Returns the description of the asset."""
        return self.info.get("asset").get("description")

    @property
    def alias(self) -> str:
        """Returns the alias of the asset."""
        return self.info.get("asset").get("alias")

    @property
    def alias_name(self) -> str:
        """Returns <class_name>/<alias> of the asset."""
        if not self.alias:
            raise exceptions.AssetException("asset does not have an alias")
        return f"{self.class_name}/{self.alias}"

    @property
    def alias_version_name(self):
        """Returns the asset name with alias and active version.

        Returns
        -------
        str
            <class_name>/<alias>/<version> or None if the asset is temporary.
        """
        if self.is_temp:
            return None
        return f"{self.alias_name}/{self.active_version}"

    @property
    def hash(self) -> str:
        """Returns the objects hash of the asset."""
        return self.info.get("asset").get("hash")

    @property
    def size(self) -> int:
        """Returns the total size of the asset in bytes."""
        return sum([file.size for file in self.files.values()], 0)

    @property
    def is_temp(self) -> bool:
        """Returns True if the asset is temporary."""
        return self.info.get('asset').get('cloning') == (False, "temp_asset")

    @cached_property
    def inputs(self) -> ArtifactInputs:
        from asset_manager import ArtifactInputs
        return ArtifactInputs(artifact=self)

    def sanitize_targets(self, targets: [str], copy_to_asset: bool = False) -> [str]:
        """
        Checks if the target files are within the asset directory, if not, then copies the files to the asset directory
        based on the force flag and returns the sanitized list of targets.
        """
        filtered_targets = []
        for target in targets:
            if os.path.isabs(target):
                if not os.path.exists(target):
                    raise exceptions.InvalidObjectSourceError(f"file {target} does not exist.")
                if not target.startswith(self.path):
                    if not copy_to_asset:
                        message = f"file {target} is outside the asset directory.\n"
                        message += "use 'copy_to_asset=True' to copy files outside the asset directory into the asset."
                        raise exceptions.AssetException(msg=message)
                    # copy the file to the asset directory and update the path
                    target = shutil.copy2(target, self.path)
            filtered_targets.append(target)
        return filtered_targets

    def add(self, targets: [str], proxy: bool = False, copy_to_asset: bool = False, force: bool = False):
        """Adds files and directories to the asset.

        Parameters
        ----------
        targets : list of str
            The files or directories to be added to the asset.
        proxy : bool, optional
            If True, files are added as proxy. This will throw an error if you are trying to add a local file as proxy.
        copy_to_asset : bool, optional
            If True, files outside the asset directory can be added to the asset.
        force : bool, optional
            If True, files will be added even if they are ignored by the .assetignore.

        Returns
        -------
        None
        """
        if proxy:
            print("adding proxy files using add(proxy=True) is getting deprecated, use add_remote() instead.")
        api = self._api.add
        with api.environment():
            # clear the info cache
            self._clear_cache(cache_name="info")
            sanitized_targets = self.sanitize_targets(targets=targets, copy_to_asset=copy_to_asset)
            with ch_dir(self.path):
                api.add_files(targets=sanitized_targets, prompt_user=False, proxy=proxy, force=force)

    def add_remote(self, targets: [str], credentials: str = None):
        """Adds remote files to the asset.

        Parameters
        ----------
        targets : list of str
            The remote file urls to be added to the asset.
        credentials : str, optional
            The credential file path to be used for accessing the remote files.

        Returns
        -------
        None
        """
        if not all([url.startswith("gs://") for url in targets]):
            raise exceptions.AssetException("only gs:// urls are supported for adding remote files")
        if credentials:
            os.environ["ASSET_CREDENTIALS"] = credentials
        api = self._api.add
        with api.environment():
            # clear the info cache
            self._clear_cache(cache_name="info")
            with ch_dir(self.path):
                api.add_files(targets=targets, prompt_user=False, proxy=True)
            # unset credentials
            if credentials:
                os.unsetenv("ASSET_CREDENTIALS")

    def set_title(self, title: str):
        """Adds a title to the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_title(title)

    def set_description(self, description: str):
        """Adds a description to the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_description(description)

    def add_alias(self, alias: str):
        """Adds an alias to the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_alias(alias=alias)

    def set_alias(self, alias: str):
        """Sets an alias for the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_alias(alias=alias)

    def remove_alias(self):
        """Removes the alias from the asset."""
        api = self._api.remove
        with api.environment():
            self._clear_cache(cache_name="info")
            api.remove_alias()

    def add_tags(self, *tags):
        """Add tags to the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_tags(tags)

    def remove_tags(self, *tags):
        """Remove tags from the asset."""
        api = self._api.remove
        with api.environment():
            self._clear_cache(cache_name="info")
            api.remove_tags(tags)

    def set_metadata(self, metadata: dict):
        """Add metadata to the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_metadata(metadata)

    def set_attributes(self, attributes: dict):
        """Add attributes to the asset."""
        api = self._api.add
        with api.environment():
            self._clear_cache(cache_name="info")
            api.add_attributes(attributes)

    def fetch(self, force=False) -> None:
        """fetches the asset metadata from remote"""
        api = FetchAPI()
        with api.environment():
            api.fetch_asset(asset_name=self.asset_name, force=force)

    def update(self) -> None:
        """updates the asset with changes"""
        api = self._api.update
        with api.environment():
            self._clear_cache()
            api.update_asset(prompt_user=False)

    def switch_version(self, version: str) -> None:
        """switches the asset to the given version"""
        api = self._api.switch
        with api.environment():
            self._clear_cache()
            api.switch_to_version(ver_number=version, ask_confirmation=False)

    def pull(self, force=False) -> None:
        """pulls the latest version of the asset"""
        api = self._api.switch
        with api.environment():
            self._clear_cache()
            api.switch_to_latest(force=force)

    def discard(self, file=None, staged=False, unstaged=False, all=True) -> None:
        """Discards all changes to the artifact

        Parameters
        ----------
        file: The specific file for which the changes are to be discarded
        staged: If true, discards - all staged file changes
        unstaged: If true discards - all unstaged file changes
        all: If true discards - all file changes

        Returns
        -------
        """

        if all:
            file = None
            staged, unstaged = False, False
        if file:
            staged, unstaged, all = False, False, False
        elif staged and unstaged:
            file = None
            all = True

        api = self._api.discard
        with api.environment():
            self._clear_cache()
            if all:
                api.discard_all_changes(ask_user=False)
            elif staged and file:
                api.discard_staged_files(file)
            elif unstaged and file:
                api.discard_unstaged_files(file)
            else:
                raise exceptions.AssetException("missing required parameter: file")

    def can_upload(self) -> bool:
        """checks if the asset can be uploaded

        Returns
        -------
        bool
        """
        api = self._api.upload
        with api.environment():
            return api.can_upload()

    def upload(self, commit_msg) -> None:
        """uploads the artifact to remote"""
        if not commit_msg:
            raise exceptions.AssetException("commit message is required for uploading asset")
        api = self._api.upload
        with api.environment():
            self._clear_cache("info")
            api.sync_to_remote(commit_msg=commit_msg)

    @classmethod
    def create(cls, class_name: str, path: str, add_files=False) -> Artifact:
        """Creates a new artifact object at the given path

        Parameters
        ----------
        class_name
        path
        add_files

        Returns
        -------
        Artifact: instance of Artifact, will throw error if there is an existing artifact

        """
        if not class_name:
            raise exceptions.AssetException("class name is required for creating a new asset")
        if not path:
            raise exceptions.AssetException("path is required for creating a new asset")
        artifact = None
        api = AssetAPI(repo=None).init
        with api.environment():
            try:
                repo_path = api.create_asset(class_name=class_name, location=path)
                if not repo_path:
                    raise exceptions.AssetException(f"unable to initialize the asset at {path}")
                artifact = Artifact(path=repo_path)
            except exceptions.AssetException as e:
                e.logs.add(f"unable to initialize the asset at {path}")
                raise
        if add_files:
            artifact.add(targets=["*"])
        return artifact

    @classmethod
    def get_or_create(cls, class_name: str, path: str, add_files=False) -> Artifact:
        """Returns an existing artifact object at the given path or creates a new artifact object at the path

        Parameters
        ----------
        class_name
        path
        add_files

        Returns
        -------
        Artifact: instance of Artifact

        """
        try:
            # check if the asset already exists at the target path
            existing = Artifact(path=path)
        except exceptions.NotAssetRepoError:
            # asset does not exist, create a new asset
            return cls.create(class_name=class_name, path=path, add_files=add_files)
        except exceptions.AssetException:
            raise

        if existing.class_name != class_name:
            raise exceptions.RepoOverwriteError(f"unable to create, found {existing.asset_name} at {path}")
        return existing

    @classmethod
    def clone(cls, name: str, path: str, soft: bool, exists_ok: bool, credentials: str = None) -> Artifact:
        """Clones an artifact at the given path.

        If an artifact already exists then throws an error.
        If the same artifact exists, then clone is skipped. This is intentional behaviour to avoid
        hitting the google/aws apis again and again if the user keeps Artifact.clone again and again or from a loop.

        Parameters
        ----------
        name : str
            Asset-name i.e. <class-name>/<seq>/<version>.
        path : str
            Directory where asset would be cloned.
        soft : bool
            If True, perform a soft clone.
        exists_ok : bool
            If True, existing asset at the target path is returned or switched to the specified version.
        credentials : str, optional
            The credential file path to be used for accessing the remote files.

        Returns
        -------
        Artifact
            Instance of Artifact after cloning.
        """
        parts = name.split("/")
        if len(parts) == 3:
            asset_name = f'{parts[0]}/{parts[1]}'
            asset_version = parts[2]
        elif len(parts) == 2:
            asset_name = name
            asset_version = None
        else:
            raise exceptions.InvalidAssetNameError(f"Invalid asset name: {name}")

        try:
            # check if the asset already exists at the target path
            existing = Artifact(path=path)
        except exceptions.AssetException:
            # no existing asset, okay to clone
            pass
        else:
            # asset exists at the target path, check for same asset
            same_asset = asset_name == existing.asset_name
            if not same_asset and existing.alias:
                # user might try to clone an asset with alias, so check for alias as well
                same_asset = asset_name == existing.alias_name
            if not same_asset:
                raise exceptions.AssetException(f"unable to clone, found {existing.asset_name} at {path}")
            # same asset but might be different version
            if exists_ok:
                if not asset_version or asset_version == existing.active_version:
                    # return the existing asset
                    return existing
                if asset_version in existing.versions:
                    # switch to the asset_version instead of cloning
                    existing.switch_version(version=asset_version)
                    return existing

        if credentials:
            os.environ["ASSET_CREDENTIALS"] = credentials
        api = CloneAssetAPI()
        with api.environment():
            asset_info = api.clone_asset(asset_name=name, target_dir=path, soft=soft)
            # unset credentials
            if credentials:
                os.unsetenv("ASSET_CREDENTIALS")
            if not asset_info:
                raise exceptions.AssetException("unable to clone asset, an unidentified error happened")

            asset_full_name, asset_full_path = list(asset_info.items())[0]
            # if version is provided, then verify the version against the cloned asset_info
            if len(name.split("/")) > 2 and asset_full_name.split("/")[2] != name.split("/")[2]:
                raise exceptions.AssetException("version mismatch, incorrect version cloned")
            return Artifact(path=asset_full_path)

    @classmethod
    def clone_or_pull(cls, name: str, path: str, soft: bool, force: bool) -> Artifact:
        """Clones an artifact at the given path.

        If an artifact already exists then pulls the latest version.

        Parameters
        ----------
        name : str
            The name of the asset to clone.
        path : str
            The location of the asset.
        force : bool, optional
            Whether to force the pull operation, by default False.

        Returns
        -------
        Artifact
            The cloned or pulled artifact object.
        """
        artifact = cls.clone(name=name, path=path, soft=soft, exists_ok=True)
        artifact.pull(force=force)
        return artifact

    @classmethod
    def find(cls, class_name: str, alias: str = None, hash: str = None) -> str:
        api = FindAPI()
        with api.environment():
            return api.find_asset(class_name=class_name, hash=hash, alias=alias)

    @classmethod
    def find_size(cls, asset_version_name: str = None) -> int:
        api = FindAPI()
        with api.environment():
            return api.find_asset_size(asset_version_name=asset_version_name, jsonize=True)

    def find_duplicates(self):
        """Finds the existing asset names with the same class name and hash."""
        existing = self.find(class_name=self.class_name, hash=self.hash)
        if existing:
            return existing.split(",")
        return None

    def find_latest_duplicate(self):
        """Finds the name of the latest duplicate asset."""
        existing = self.find_duplicates()
        if not existing:
            return None
        if len(existing) == 1:
            return existing[0]

        # Custom key function to sort by integer id and then version
        def sort_key(name):
            # Split the string by '/' and extract parts
            parts = name.split('/')
            return parts[0], int(parts[1]), tuple(map(int, parts[2].split(".")))

        # Sort the existing assets by the custom key function
        existing.sort(key=sort_key)
        return existing[-1]

    @classmethod
    def fetch_asset_class(cls, asset_name=None, class_name=None, force=False) -> None:
        """fetches metadata from remote"""
        if not asset_name and not class_name:
            raise exceptions.AssetException("missing required parameter: asset_name or class_name")

        api = FetchAPI()
        with api.environment():
            if asset_name:
                api.fetch_asset(asset_name=asset_name, force=force)
            else:
                api.fetch_assets(class_name=class_name, force=force)

    @classmethod
    def asset_name_exists(cls, name: str):
        """Validates the asset name and check if it exists in the remote."""
        api = FindAPI()
        with api.environment():
            handle = AssetHandle.from_name(asset_name=name)
            fetcher = AssetFetcher(store=AssetStore.shared())
            # check if the asset is valid
            if not handle.is_valid(fetcher=fetcher, find_api=api):
                raise exceptions.InvalidAssetNameError(f"invalid seq_id:{handle.seq_id} or version:{handle.version}")
            # check if the asset exists in the remote
            return fetcher.verify_asset_exists(class_id=handle.class_id, seq_id=handle.seq_id, version=handle.version)

    def exists(self):
        """Validates the asset and check if it exists in the remote."""
        return self.__class__.asset_name_exists(name=self.asset_version_name)

    @classmethod
    def copy(cls, src: str, dst: str, recursive=False, force=False, skip_cmp=False, credentials=None):
        """asset cp command"""
        if credentials:
            os.environ["ASSET_CREDENTIALS"] = credentials
        api = CopyAPI()
        with api.environment():
            api.copy(src=src, dst=dst, recursive=recursive, force=force, skip_cmp=skip_cmp)
            # unset credentials
            if credentials:
                os.unsetenv("ASSET_CREDENTIALS")

    def file_url(self, file_path: str) -> str:
        """Returns the dashboard URL of the file in the asset.

        The file_path should be relative to the asset root directory.
        """
        if not file_path:
            raise exceptions.AssetException("missing required parameter: file_path")

        api = self._api.info
        with api.environment():
            return api.print_object_url(rel_file_path=file_path, jsonize=True)
