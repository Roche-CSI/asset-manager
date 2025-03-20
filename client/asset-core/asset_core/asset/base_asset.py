import abc
import math
import os

from asset_core.plugins import utils, list_files, FileUtils, LoggingMixin


class BaseAsset(LoggingMixin):
    """Base Asset class controls all paths and urls, so that we can
    perform all meta operations on asset without creating the asset which is a heavy object
    """
    id: str = None
    seq_id: int = None
    repo = None
    asset_class = None

    def __init__(self,
                 id=None,
                 seq_id=None,
                 repo=None,
                 asset_class=None
                 ):
        self.id = id
        self.seq_id = seq_id
        self.repo = repo
        self.asset_class = asset_class
        self.asset_class.repo = repo

    @property
    def linked_dir(self):
        """Linked dir of the asset, this is typically same as the repo dir.
        But the user can override this by passing assets download --target
        # todo: save target dir in a yaml file
        # todo: discuss if the target dir should be stored as part of manifest or the state.yaml
        """
        return self.repo.fs_path

    @property
    def repo_dir(self):
        return self.repo.fs_path

    @property
    def remote_url(self):
        if self.id and self.seq_id and self.asset_class.id:
            return self.repo.store.asset_url(class_id=self.asset_class.id, seq_id=self.seq_id)
        return None

    @property
    def name(self):
        """asset_class_name/seq_id"""
        if not self.seq_id:
            raise Exception("seq_id can not be null")

        return f"{self.asset_class.name}/{str(self.seq_id)}"

    @classmethod
    def parse_name(cls, name):
        """return class_name and seq_id from name"""
        if not name:
            raise Exception("asset name can not be null")
        try:
            parts = name.split("/")
            # user can sometimes miss the forward slash while typing
            if len(parts) == 2:
                return parts
            else:
                return None
        except ValueError as e:
            cls.logger().info(str(e))
            return None

    @property
    @abc.abstractmethod
    def contents_cache_dir(self):
        raise NotImplementedError

    @property
    def cache_dir(self):
        if not self.seq_id:
            raise Exception("asset not uploaded yet")
        return os.path.join(self.asset_class.cache_dir, str(self.seq_id))

    @property
    def states_file(self):
        if not self.id:
            return None
        return self.__class__.states_path(repo=self.repo,
                                          asset_id=self.id,
                                          version=self.version.number)

    @property
    def manifest_file(self):
        if not self.id:
            return None
        return self.__class__.manifest_path(repo=self.repo,
                                            asset_id=self.id,
                                            version=self.version.number)

    @classmethod
    def manifest_path(cls, repo, asset_id, version):
        return os.path.join(repo.manifests_dir, asset_id, f"{version}.yaml")

    @classmethod
    def states_path(cls, repo, asset_id, version):
        return os.path.join(repo.states_dir, asset_id, f"{version}.yaml")

    def cached_versions(self):
        version_yamls = list_files(root_dir=self.cache_dir, pattern="version*.yaml")
        data = []
        for version in version_yamls:
            data.append(FileUtils.read_yaml(version))
        # sort by ascending i.e earliest to latest
        data.sort(key=lambda x: x.get("id"))
        return data

    def cached_objects(self):
        objects_yaml = os.path.join(self.cache_dir, "objects.yaml")
        if not os.path.exists(objects_yaml):
            return None
        return FileUtils.read_yaml(objects_yaml).get("objects")

    def cached_asset_data(self):
        if self.__class__.is_temp_seq_id(self.seq_id):
            # local asset so no cached data
            return {}
        return self.asset_class.list_assets().get(int(self.seq_id))

    @classmethod
    def generate_temp_seq_id(cls):
        return f"temp_{math.floor(utils.time_now().timestamp())}"

    @classmethod
    def is_temp_seq_id(cls, seq_id):
        if type(seq_id) is int:
            return False
        if type(seq_id) is str and str(seq_id).startswith("temp_"):
            return True
        return False

    @property
    def is_temp(self):
        class_name, seq_id = self.__class__.parse_name(self.name)
        return self.__class__.is_temp_seq_id(seq_id)

    @classmethod
    def get_id(cls, data):
        return data.get("id")
