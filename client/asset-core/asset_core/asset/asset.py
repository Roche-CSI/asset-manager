from __future__ import annotations

import fnmatch
import math
import os
import uuid
from typing import Optional

from cached_property import cached_property

from asset_core.objects.asset_object import AssetObject, ObjectViews
from asset_core.objects.object_factory import ObjectFactory
from asset_core.plugins import utils, FileUtils, Progress, exceptions
from asset_db import ManifestDB, FileDB, StatesDB, StoreFileDB
from asset_utils.utils.path_utils import PathUtils
from .asset_class import AssetClass
from .asset_version import AssetVersion
from .refs.asset_ref import AssetRef
from .serializable_asset import SerializableAsset
from .state import AssetState


class Asset(SerializableAsset):
    views = AssetObject.views
    repo = None
    states = AssetState
    TEMP_SEQ_PREFIX = "temp_"
    view: ObjectViews = None

    def __init__(self, repo=None, id=None, load=True, view=None):
        super().__init__(id=id)
        self.auto_save = False
        self.repo = repo
        self.view = view or self.views.DATA  # default to DATA always
        if load:
            # default to current asset, if the user has not provided
            self.assign_current_asset()
            # load from manifest file
            self.de_serialize()
            # legacy support - repo.json doesn't have linking type
            if not self.repo.linking_type:
                self.repo.linking_type = self.infer_linking_type()
        self.auto_save = True

    def assign_current_asset(self):
        """assigns the repos current asset as active asset"""
        if not self.repo:
            return
        asset_data = self.repo.current_asset
        if not asset_data:
            return
        self.id = asset_data.get("id")
        self.seq_id = asset_data.get("seq_id")
        self.asset_class.de_serialize(asset=self, data=asset_data.get("asset_class", {}))
        self.version.de_serialize(asset=self, data=asset_data.get("version", {}))

    @classmethod
    def create_new(cls, repo, class_name, class_id, project=None):
        if not class_id or not class_name:
            raise exceptions.AssetClassNotFoundError()
        repo.current_asset = {}
        asset = Asset(repo=repo, load=False)
        asset.auto_save = False
        asset.id = Asset.new_id()
        asset.seq_id = Asset.generate_temp_seq_id()
        asset.version.number = asset.seq_id  # use a temp version
        asset.asset_class.name = class_name
        asset.asset_class.id = class_id
        asset.asset_class.project = project or repo.store.project_id
        asset.created_at = utils.convert_to_pst(utils.time_now())
        asset.created_by = repo.store.user_id
        asset.owner = asset.created_by
        asset.save()
        asset.auto_save = True
        asset.set_state(asset.states.PENDING, save=True)
        # repo management
        asset.set_as_current()
        asset.add_to_templist()
        return asset

    @classmethod
    def retrieve(cls, repo, asset_name) -> Asset:
        class_name, seq_id = cls.parse_name(asset_name)
        # if it's an uncommitted asset then we just verify if the asset name is correct
        if Asset.is_temp_seq_id(seq_id):
            return cls.retrieve_temp_asset(repo=repo,
                                           class_name=class_name,
                                           seq_id=seq_id)

        if not Asset.is_valid_seq_id(seq_id):
            raise exceptions.InvalidAssetNameError()

        asset = Asset(repo=repo, load=False)
        # get the asset class, this will throw ClassNotFoundError if class not present locally
        asset_class = AssetClass.get_asset_class(store=repo.store, name=class_name)
        # we need seq_id to find the file
        asset.seq_id = seq_id
        asset.asset_class = asset_class
        cached = asset.cached_asset_data()
        cached.pop('asset_class')
        asset.de_serialize(data=cached)
        # reassign, serialization
        if not asset.id:
            raise exceptions.AssetNotFoundError()
        return asset

    @classmethod
    def retrieve_temp_asset(cls, repo, class_name, seq_id) -> Asset:
        # verify the temp asset exists
        temp_assets = repo.store.list_temp_assets(class_name=class_name)
        asset_data = temp_assets.get(seq_id)
        if not asset_data:
            raise exceptions.InvalidAssetNameError()
        asset = Asset(repo=repo)
        asset.de_serialize(data=asset_data)
        if not asset.id:
            raise exceptions.AssetNotFoundError()
        return asset

    @classmethod
    def new_id(cls):
        return str(uuid.uuid4())

    def set_as_current(self, repo=None):
        repo = repo or self.repo
        repo.current_asset = self._table_data()

    def add_to_templist(self):
        """adds the asset to list of local assets i.e. assets that don't exist
        in the remote yet.
        """
        self.repo.add_to_temp_assets(self.asset_class.name, self._table_data())

    def _table_data(self):
        """returns display data for the asset"""
        return {
            "id": self.id,
            "asset_class": self.asset_class.serialize(),
            "seq_id": self.seq_id,
            "owner": self.owner,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "top_hash": self.top_hash,
            "status": self.status,
            "version": self.version.serialize()
        }

    def get_state(self):
        try:
            return self._state
        except AttributeError:
            self._state = self.states_db.get_asset_state()
            return self._state

    def set_state(self, x, save=False):
        self._state = x
        if save:
            self.states_db.set_asset_state(x)

    def can_commit(self):
        state = self.get_state()
        if not state or state == self.states.COMMITTED:
            return False
        return True

    @property
    def project_id(self):
        if not self.asset_class.project:
            self.assign_current_asset()
        return self.asset_class.project

    @property
    def commit_message(self):
        # commit message is part of the states_db since it applies to current changes
        # which is captured by states_db
        return self.states_db.get_commit_message()

    @commit_message.setter
    def commit_message(self, x):
        self.states_db.set_commit_message(x)

    @property
    def db(self) -> ManifestDB | None:
        if self.manifest_file:
            return ManifestDB(path=self.manifest_file)
        return None

    @cached_property
    def object_stats_db(self) -> FileDB:
        return FileDB(path=self.repo.objects_stats_file)

    @cached_property
    def content_stats_db(self) -> StoreFileDB:
        return StoreFileDB(self.asset_class.content_stats_file)

    @property
    def states_db(self) -> StatesDB:
        return StatesDB(path=self.states_file)

    @property
    def hash(self):
        # todo: implement
        raise NotImplementedError
        # object_ids = list(map(lambda x: x.id, self.objects))
        # return FileUtils.string_md5(",".join(sorted(object_ids)))

    def filter_objects(self, attr: str, values: list) -> [AssetObject]:
        """returns a dict of assets stored in asset-manifest
        Parameters:
            attr: attribute i.e. id, path, hash of the asset_object
            values: the list of values to match. for example: {ht: [md5, crc]}
        """
        if not attr or not values:
            return []
        return [obj for obj in self.objects if getattr(obj, attr) in values]

    def remove_objects(self, targets: [AssetObject], delete=False):
        """Deletes a given list of objects
        1. remove from asset-manifest
        2. delete from the directory, the default behaviour is objects are removed from the asset only
        Parameters:
            targets list of AssetObject instances
        """
        if not targets:
            return
        # 1. remove from objects and asset_objects
        self.objects.remove_objects(targets, save=True)  # remove without error
        for obj in targets:
            obj.unlink(delete=delete)

        # reset the state to pending
        if self.get_state() != self.states.PENDING:
            self.set_state(self.states.PENDING, save=True)

    def create_and_add_objects(self,
                               data: dict,
                               object_type: str = None,
                               p_bar: Progress = None,
                               proxy: bool = False):
        """
        Creates and adds new objects to the asset. Creating is the computationally more expensive.
        Since user has the option to cancel anytime (ctrl+c), we need to preserve atomicity for such cancellation events.
        Therefore -  we perform the action in 2 different steps
        1. bulk create (as opposed to individual create/add) operations
        2. bulk add/update

        Parameters
        ----------
        data: dict
            {storage_name: [object_sources]}
        object_type: str
        p_bar: Progress
        proxy: bool. if true, the content is added as a proxy

        """
        if not data:
            raise exceptions.InvalidObjectSourceError("invalid object source")

        for source in data:
            if not data[source]:
                raise exceptions.InvalidObjectSourceError("invalid object source")

        if p_bar:
            p_bar.set_description("creating objects", refresh=True)

        new_objects = ObjectFactory().bulk_create(source_data=data,
                                                  repo_dir=self.repo_dir,
                                                  object_type=object_type,
                                                  proxy=proxy,
                                                  callback=lambda x: p_bar.update(
                                                      int(bool(x))) if p_bar else None
                                                  )
        if p_bar:
            p_bar.close("done")

        if not new_objects:
            raise exceptions.InvalidObjectSourceError("invalid object source")

        self.update_state(new_state=self.states.PENDING)
        added, updated, ignored = self.add_objects(objects=new_objects, show_progress=bool(p_bar))
        return added, updated, ignored

    def update_state(self, new_state: AssetState):
        current_state = self.get_state()
        if not current_state or current_state == self.states.COMMITTED:
            self.set_state(new_state, save=True)
            self.commit_message = None  # reset commit message

    def add_objects(self, objects: [AssetObject], show_progress: bool = False):
        """Creates Objects out of files and adds to asset-manifest

        Parameters
        ----------
        objects: [Object]
            list of Objects
        show_progress: bool
            if true, show progress bar
        """
        if self.frozen:
            raise exceptions.AssetException("asset is frozen, no more files can be added to it")
        if not objects:
            return
        p_bar = None
        if show_progress:
            # restart from next line
            p_bar = Progress.progress_bar(total=len(objects))
            p_bar.set_description("updating object cache", refresh=True)

        def update(x):
            if p_bar:
                p_bar.update(int(bool(x)))

        try:
            new_objects, updates, ignored = self.objects.add_objects(objects, save=True, callback=update)
            if p_bar:
                p_bar.close("done")
        except Exception as e:
            if p_bar:
                p_bar.close("error")
            raise e

        return new_objects, updates, ignored

    def create_and_add_ref(self,
                           src_name: str,
                           label: str,
                           properties: dict) -> tuple:
        """Creates and adds asset ref

        Parameters
        ----------
        src_name: str
                source version name i.e <class>/<seq_id>/<version_number>
        label: str
            ref label
        properties
            ref properties

        Returns
        -------
        tuple
            (added, existing)
        """
        ref_comps = AssetVersion.parse_name(src_name)
        class_name, seq_id = [ref_comps.get(k) for k in ["class_name", "seq_id"]]
        if self.asset_name(class_name=class_name, seq_id=seq_id) == self.name:
            raise exceptions.ForbiddenRefError(f"can not create input: {src_name}, asset can not reference itself")
        dst_version = self.root_version()  # currently we support adding refs to the root version only
        ref = AssetRef.create(
            asset=self,
            src_ver_name=src_name,
            dst_ver_name=dst_version.name,
            dst_ver_id=dst_version.id,
            label=label,
            properties=properties
        )
        return self.add_refs([ref])

    def add_refs(self, refs: [AssetRef]) -> tuple:
        """creates Objects out of files and adds to asset-manifest
        Parameters
        ----------
        refs
        """
        if not refs:
            return [], []

        added, existing = self.refs.add_refs(refs=refs, save=True)
        return added, existing

    def remove_refs(self, targets: [AssetRef]):
        """Deletes a given list of refs
        1. remove from asset-manifest
        2. delete from the directory, the default behaviour is objects are removed from the asset only
        Parameters:
            targets list of AssetObject instances
        """
        if not targets:
            return
        # 1. remove from objects and asset_objects
        self.refs.remove_refs(refs=targets, save=True)  # remove without error

        # reset the state to pending
        if self.get_state() != self.states.PENDING:
            self.set_state(self.states.PENDING, save=True)

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
            raise exceptions.AssetException("seq_id can not be null")
        return self.__class__.asset_name(class_name=self.asset_class.name,
                                         seq_id=self.seq_id)

    @classmethod
    def asset_name(cls, class_name, seq_id):
        return os.path.join(class_name, str(seq_id))

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
                raise exceptions.InvalidAssetNameError()
        except ValueError as e:
            raise exceptions.InvalidAssetNameError(str(e))

    @property
    def contents_cache_dir(self):
        return self.asset_class.content_cache_dir

    @property
    def cache_dir(self):
        if self.is_temp:
            raise exceptions.AssetException("asset not uploaded yet")
        return os.path.join(self.asset_class.cache_dir, str(self.seq_id))

    @property
    def snapshots_dir(self):
        return os.path.join(self.cache_dir, "objects_snapshots")

    @property
    def snapshot_file(self):
        return os.path.join(self.snapshots_dir, f"{self.version.number}.json")

    @property
    def states_file(self):
        if not self.id:
            return None
        return self.__class__.states_path(repo=self.repo, asset_id=self.id, version=self.version.number)

    @property
    def manifest_file(self):
        if not self.id or not self.repo or not self.version.number:
            return None
        return self.__class__.manifest_path(repo=self.repo, asset_id=self.id, version=self.version.number)

    @property
    def cached_manifest_file(self):
        if not self.id or not self.repo or not self.version.number:
            return None
        return self.repo.store.cached_manifest_file(asset_id=self.id, ver_number=self.version.number)

    def cached_manifest_data(self):
        if self.is_temp:
            return {}
        if not os.path.exists(self.cached_manifest_file):
            # create
            return {}
        return FileUtils.read_json(self.cached_manifest_file)

    @classmethod
    def manifest_path(cls, repo, asset_id, version):
        return os.path.join(repo.manifests_dir, asset_id, f"{version}.json")

    @classmethod
    def states_path(cls, repo, asset_id, version):
        return os.path.join(repo.states_dir, asset_id, f"{version}.json")

    def cached_versions(self) -> list:
        """Returns a sorted list of all the versions of the asset."""
        version_yamls = utils.list_files(root_dir=self.cache_dir, pattern="version*.yaml")
        data = []
        for version in version_yamls:
            data.append(FileUtils.read_yaml(version))
        # sort by ascending i.e. earliest to latest
        data.sort(key=lambda x: x.get("id"))
        return data

    def root_version(self) -> AssetVersion:
        if self.is_temp:
            return self.version
        root = AssetVersion()
        root.de_serialize(asset=self, data=self.cached_versions()[0])
        return root

    def list_objects(self, ver_number: str = None, pattern: str = None) -> [AssetObject]:
        if not ver_number or ver_number == self.version.number:
            objects = [obj for obj in self.objects]  # return from current version
        else:
            new_asset = self.deep_copy(ver_number=ver_number)
            objects = [obj for obj in new_asset.objects]

        if pattern:
            objects = [obj for obj in objects if fnmatch.fnmatch(obj.path, pattern)]

        return objects

    def deep_copy(self, ver_number: str = None, view: ObjectViews = None) -> Asset:
        """returns a deep copy of the asset for the specific version"""
        from asset_core.asset.asset_diff import AssetDiff
        ver_number = ver_number or self.version.number
        duplicate = Asset(repo=self.repo, id=self.id, load=False, view=view or self.view)
        duplicate.asset_class = self.asset_class
        duplicate.seq_id = self.seq_id
        if ver_number and ver_number == self.version.number:
            manifest_file = self.manifest_file
        else:
            manifest_file = AssetDiff().create_asset_manifest(asset=duplicate, ver_number=ver_number)
        duplicate.de_serialize(data=FileUtils.read_json(manifest_file))
        duplicate.top_hash = self.top_hash
        return duplicate

    def get_object(self, object_path: str, ver_number: str) -> Optional[AssetObject]:
        objects: [AssetObject] = self.list_objects(ver_number=ver_number)
        for obj in objects:
            if obj.path == object_path:
                return obj
        return None

    def cached_objects(self) -> dict:
        objects_dir = os.path.join(self.cache_dir, "objects")
        if not os.path.exists(objects_dir):
            return {}
        objects = FileUtils.read_yaml_dir(objects_dir)
        result = {}
        for object in objects.values():
            result[object.get("id")] = object
        return result

    def cached_objects_v2(self, dir: str = None) -> dict:
        objects_dir = dir or os.path.join(self.cache_dir, "objects_v2")
        if not os.path.exists(objects_dir):
            return {}
        objects = FileUtils.read_json_zip_dir(objects_dir)
        result = {}
        for obj in objects:
            result[obj.get("id")] = obj
        return result

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
        if type(seq_id) is str and str(seq_id).startswith(cls.TEMP_SEQ_PREFIX):
            return True
        return False

    @classmethod
    def is_valid_seq_id(cls, seq_id):
        return bool(type(seq_id) is int or str(seq_id).isnumeric())

    @property
    def is_temp(self):
        class_name, seq_id = self.__class__.parse_name(self.name)
        return self.__class__.is_temp_seq_id(seq_id)

    @classmethod
    def get_id(cls, data):
        return data.get("id")

    @classmethod
    def get_name(cls, data: dict):
        if not data:
            return
        asset_class = data.get("asset_class")
        return cls.asset_name(class_name=asset_class.get("name"),
                              seq_id=data.get("seq_id"))

    def infer_linking_type(self) -> str:
        # newly created asset, use default (copy)
        if self.is_temp or not self.objects:
            return "copy"

        for obj in self.objects:
            # get a non-proxy object to infer the linking type
            if obj.linked():
                return PathUtils.path_link_type(obj.linked_path)

        # no non-proxy object found, use default (copy)
        return "copy"
