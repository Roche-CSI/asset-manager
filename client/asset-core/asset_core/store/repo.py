"""Repo is where your asset lives. To access an asset you must be inside the Repo
directory that contains the asset. You can either create a repo using asset init or asset clone.
The Repo class provides the following functionalities.
* __init__: it checks if the cwd is inside a valid Repo directory, we do this by traversing the directory
  tree upward until we find the Repo signature which is '.asset' directory. For more details see the __init__
  description.
* create_repo: it creates a repo at the cwd.
* validate_repo: Verifies if the repo is valid. The Repo object needs some meta information in order to manage the
  asset. These meta information are saved inside the asset_store
* maintains the storage paths for the asset

* Note: Why we store repo meta information inside the asset_store and not inside the repo directory.
  The user has direct access to the repo directory and therefore can either move, copy or delete the repo directory.
  This will induce a bug into the asset management flow because we use a single global store (see AssetStore class
  for reasons why use a global store). For example, if user makes a copy of the repo_dir or moves it to a new location
  - it affects our reference counting of objects which is essential for storage optimization. It will also bugs in
  asset fetch because we will no longer be able to update the local asset with new updates from remote (since the user
  has altered its location).

  To prevent these problems, we use the following information storage architecture
  - Repo directory has a .asset directory which is the signature of a valid asset repo
  - Inside 'repo_dir/.asset', there is a '*.id' file, which points to the unique id for that repo.
  - All meta information for a specific repo is stored inside 'asset_store/repos/repo_id' directory
  - When a Repo class is instantiated, it verifies if its id is pointing to the correct path, if not -
    then the user may have copied or moved or deleted. We then perform the necessary repo migration
    steps before proceeding (For details see verify_repo)
"""
import os
import uuid

from asset_core.configs import Configs
from asset_core.store.asset_store import AssetStore
from asset_db import RepoDB
from asset_utils.common import exceptions
from asset_utils.utils import list_files
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin
from asset_utils.utils.path_utils import PathUtils


class Repo(LoggingMixin):
    _root: str = None
    _instance = None
    store: AssetStore = None

    def __init__(self, root=None, validate=True):
        """Initialize the Repo object.

        Set the validation flag to False while calling from inside
        validate_repo to avoid recursion.
        """
        self._root = root
        if not self._root:
            self._root = self.__class__.find_root()
        self.store = AssetStore.shared(create_if_not_exists=True)
        if validate:
            self.validate_repo()

    def validate_repo(self):
        """Validates the repo.

        - Validate the path to check if it's nested with another repo
        - Validate the store.json file which tracks all the repos
        """
        # check if the repo is nested inside another repo
        self.check_inside_repo()
        # check if the repo contains another repo
        self.check_contains_repo()
        # validate the repo with the store.json file
        self.validate_store_repos()

    def validate_store_repos(self):
        """Validates the repo with the store.json file

        We maintain a global asset store.json file that tracks all the repos.
        Its important that every repo has a unique id.

        When a  repo is created, we also create a pointer in the store for that repo. But the pointer accuracy
        is affected, if:
         - User moves the repo directory (in this case the repo path stored in the pointer is no longer valid)
         - User makes a copy of the repo directory (here the same repo id is now shared by multiple repo paths)
         """
        repo_data = self.store.repo_data(self.id)
        if repo_data:
            if os.path.samefile(repo_data.get("path"), self.fs_path):
                # the repo is valid, no need to do anything further
                return
            else:
                # change detected, further checking is needed
                # prune the store to remove invalid repos before proceeding
                self.store.prune_repos()
                # update the repo data after pruning
                repo_data = self.store.repo_data(self.id)

        # we are inside an invalid repo that has an id
        # if we still get the repo data, then it's a copy
        if repo_data:
            # create a new repo id and update both store.json and repo.json inside the repo
            self.clear_id(repo_root=self.fs_path, id=self.id)
            self._id = self.create_new_id(repo_root=self.fs_path)
            self.store.add_repo(repo_id=self._id, data={"path": self.fs_path})
        else:
            # user has moved the repo manually
            # before adding, check if the path is pointing to any existing repo
            # Scenario: assetA in dir1 and assetB is in dir2
            #   user deletes assetB and then moves assetA to dir2
            #   now store.json has assetB.repo.id pointing to dir2
            #   we need to correct this by deleting the assetB entry and adding assetA entry
            for repo_id, data in self.store.list_repos().items():
                if os.path.samefile(data.get("path"), self.fs_path):
                    # remove the existing entry from the store
                    self.store.remove_repo(repo_id=repo_id)
            # add the repo to the store with existing id
            self.store.add_repo(repo_id=self.id, data={"path": self.fs_path})

    def check_inside_repo(self):
        """Check if the current directory is inside another repo"""
        search_dir = os.path.dirname(self.fs_path)
        # move up to get rid of non-existent directories
        while not os.path.exists(search_dir):
            search_dir = os.path.dirname(search_dir)
        try:
            outer_repo = self.find_root(root=search_dir)
        except exceptions.NotAssetRepoError:
            return

        if outer_repo:
            message = "nested inside another asset"
            # we found the outer repo, no need to validate again
            outer_repo = Repo(root=outer_repo, validate=False)
            outer_asset = outer_repo.current_asset
            if outer_asset:
                # append the name of the outer_asset
                message += f": {outer_asset['asset_class']['name']}/{outer_asset['seq_id']}"
            # add repo to the error data for further usage
            raise exceptions.NestedRepoError(msg=message, data={"repo": outer_repo})

    def check_contains_repo(self):
        """Check if the current directory contains another repo.

        TODO: No need to get all the matching files/directories.
            Just getting the first matching directory is enough.
            use asset_utils.utils.first_matching_dir for that
        """
        files = list_files(self.fs_path, pattern="*/.asset/*")
        if files:
            message = "already contains an asset"
            inner_repo = files[0].split("/.asset")[0]
            # we found the inner repo, no need to validate again
            inner_repo = Repo(root=inner_repo, validate=False)
            inner_asset = inner_repo.current_asset
            if inner_asset:
                # append the name of the inner_asset
                message += f": {inner_asset['asset_class']['name']}/{inner_asset['seq_id']}"
            # add repo to the error data for further usage
            raise exceptions.NestedRepoError(msg=message, data={"repo": inner_repo})

    @classmethod
    def id_file(cls, repo_root, id):
        return AssetStore.id_file(repo_root=repo_root, repo_id=id)

    @classmethod
    def is_valid(cls, path, id):
        return AssetStore.is_valid_repo(path=path, repo_id=id)

    @classmethod
    def create_new_id(cls, repo_root):
        # if an id exists then throw error, must delete existing id before creating new
        if Repo._find_id(location=repo_root):
            raise exceptions.RepoOverwriteError(data={"location": repo_root})
        new_id = str(uuid.uuid4())
        FileUtils.create_file_if_not_exists(Repo.id_file(repo_root=repo_root, id=new_id))
        return new_id

    @classmethod
    def clear_id(cls, repo_root, id):
        """removes the existing id"""
        id_file = cls.id_file(repo_root=repo_root, id=id)
        if os.path.exists(id_file):
            os.remove(id_file)

    @property
    def id(self):
        try:
            return self._id
        except AttributeError:
            self._id = self.__class__._find_id(location=self.__class__.repo_asset_dir(repo_root=self.fs_path))
            if not self._id:
                raise exceptions.NotAssetRepoError("repo id missing")
            return self._id

    @classmethod
    def repo_asset_dir(cls, repo_root: str):
        """.asset dir inside the repo"""
        return os.path.join(repo_root, Configs.shared().asset.asset_dir)

    def normalize_filepath(self, path):
        return os.path.relpath(os.path.abspath(path), start=self.fs_path)

    @classmethod
    def _find_id(cls, location: str):
        """
        Parameters
        ----------
        location: <dirname>/<.asset>, we are looking for a .id file here

        Returns
        -------

        """
        # verify parent exists
        parent_dir = os.path.dirname(location)
        if not os.path.exists(parent_dir):
            raise exceptions.NotAssetRepoError(f"invalid path: {parent_dir} doesn't exist")

        try:
            files = list_files(location, pattern="*.id", recurse=False)
            if not files or len(files) > 1:
                return None
            return os.path.splitext(os.path.basename(files[0]))[0][1:]  # remove the dot

        except FileNotFoundError:
            raise exceptions.NotAssetRepoError(f"no asset repo found at: {parent_dir}")

    # noinspection PyMethodMayBeStatic
    def _exists(self, root):
        if not root:
            return False
        if not os.path.exists(root) or not os.path.isdir(root):
            return False

    def __str__(self):
        return self._root

    @property
    def current_asset(self) -> dict:
        try:
            return self._current_asset
        except AttributeError:
            self._current_asset = self.db.get("current_asset") or {}
            return self._current_asset

    @current_asset.setter
    def current_asset(self, x: dict):
        self._current_asset = x
        self.db.add(**{"current_asset": x})
        # add the new asset
        repo_data = self.store.repo_data(repo_id=self.id)
        repo_data["asset"] = self._current_asset.get("id") if self._current_asset else None
        self.store.add_repo(repo_id=self.id, data=repo_data)

    @property
    def linking_type(self):
        try:
            return self._linking_type
        except AttributeError:
            self._linking_type = self.db.get("linking_type")
            return self._linking_type

    @linking_type.setter
    def linking_type(self, x: str):
        self._linking_type = x
        self.db.add(**{"linking_type": x})

    def add_to_temp_assets(self, class_name, asset_data):
        self.store.add_to_temp_assets(class_name=class_name, asset_data=asset_data)

    def remove_from_temp_assets(self, seq_id, class_name):
        self.store.remove_from_temp_assets(seq_id=seq_id, class_name=class_name)

    def list_temp_assets(self, class_name) -> dict:
        return self.store.list_temp_assets(class_name=class_name)

    def get_temp_asset_id(self, asset_name: str):
        return self.store.get_temp_asset_id(asset_name)

    @property
    def db(self):
        return RepoDB(self.repo_file)

    @property
    def fs_path(self):
        """ absolute path of the repo"""
        return os.fspath(self._root)

    @property
    def meta_dir_legacy(self):
        """Legacy implementation of meta dir, needed for backward compatibility"""
        return self.store.repo_meta_dir(self.id)

    @property
    def meta_dir(self):
        new_meta_dir = os.path.join(self.fs_path, self.asset_dir(), "repo")
        if not os.path.exists(new_meta_dir):
            # migrate the meta_dir from store to new_meta_dir
            self.migrate_meta_dir(new_meta_dir)
        return new_meta_dir

    def migrate_meta_dir(self, new_meta_dir):
        """Migrate metadata to new meta dir"""
        if os.path.exists(self.meta_dir_legacy):
            os.makedirs(new_meta_dir, exist_ok=True)
            FileUtils.hardlink_directories(src_dir=self.meta_dir_legacy, dst_dir=new_meta_dir)
            # TODO: remove the legacy meta dir after a few releases

    @property
    def states_dir(self):
        return os.path.join(self.meta_dir, Configs.shared().asset.states_dir)

    @property
    def manifests_dir(self):
        return os.path.join(self.meta_dir, Configs.shared().asset.manifests_dir)

    @property
    def repo_file(self):
        return os.path.join(self.meta_dir, Configs.shared().asset.repo_file)

    @property
    def objects_stats_file(self):
        return os.path.join(self.meta_dir, Configs.shared().asset.content_stats_file)

    def contents_url(self, staging) -> str:
        return self.store.contents_url(staging=staging)

    @property
    def assets_url(self):
        return self.store.assets_url

    def asset_class_url(self, class_id):
        return os.path.join(self.assets_url, class_id)

    # noinspection PyPropertyDefinition
    @classmethod
    def asset_dir(cls):
        """Returns the path to assets directory."""
        return Configs.shared().asset.asset_dir

    @classmethod
    def find_root(cls, root=None, fs=None) -> str:
        """User can add files from a subdirectory of the project.

        By default - we check in the current directory first
        if there is a .assets dir, then that's the root and we return.
        If we don't find, we keep going up in the directory tree until we find a .assets
        """
        root_dir = os.path.realpath(root or os.getcwd())
        if fs:
            asset_dir = os.path.join(root_dir, cls.asset_dir())
            if fs.isdir(asset_dir):
                return root_dir
            raise exceptions.NotAssetRepoError(f"'{root}' does not contain {cls.asset_dir()} directory")

        if not os.path.isdir(root_dir):
            raise exceptions.NotAssetRepoError(f"directory '{root}' does not exist")

        # do an upward recursion in case the user is in a subdirectory while trying to add_assets
        while True:
            asset_dir = os.path.join(root_dir, cls.asset_dir())
            if os.path.isdir(asset_dir):
                return root_dir
            if os.path.ismount(root_dir):
                break
            root_dir = os.path.dirname(root_dir)

        raise exceptions.NotAssetRepoError(
            f"you are not inside an Assets repository (checked up to mount point '{root_dir}')")

    @staticmethod
    def create_repo(root_dir=os.curdir, force=False):
        """
        Creates an empty repo on the given directory -- basically a
        `.assets` directory that holds all the assets.

        :param root_dir: Path to repo's root directory
        :param force: if true, then the existing asset directory is deleted
        :return: instance of Repo class
        """
        root_dir = os.path.realpath(root_dir)
        assets_dir = os.path.join(root_dir, Repo.asset_dir())
        if os.path.isdir(assets_dir):
            if not force:
                raise exceptions.AssetException(f"unable to create asset repo, '{assets_dir}' exists")
            PathUtils.remove(assets_dir)

        os.makedirs(assets_dir, exist_ok=True)
        # clear any existing id
        repo_id = Repo.create_new_id(repo_root=root_dir)
        # update store
        store = AssetStore.shared()
        store.add_repo(repo_id=repo_id, data={"path": root_dir})
        repo = Repo(root=root_dir)
        repo.db.add(**{"repo_id": repo_id})
        return repo
