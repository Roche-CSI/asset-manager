from __future__ import annotations

import os

from asset_pluggy.storage import Transporter
from asset_pluggy.storage.storage_factory import StorageFactory
from asset_utils.utils.in_memory_file import InMemoryFile
from peewee import *
from playhouse.postgres_ext import JSONField

from server_core.asset_client import exceptions
from server_core.asset_client import versioning
from server_core.models import asset as asset_model
from server_core.models import asset_class
from server_core.models.base import read_only


class AssetVersion(read_only.ReadOnlyModel):
    id = BigAutoField(primary_key=True)
    asset = ForeignKeyField(asset_model.Asset, backref='versions', null=False, on_delete='CASCADE')  # root
    number = CharField(null=False)
    patch = JSONField(default=dict, null=True)
    parent = ForeignKeyField('self', backref='child', null=True)
    commit_hash = CharField(max_length=100, null=True)
    commit_message = TextField(null=True)
    size = BigIntegerField(null=True, default=None)
    num_objects = IntegerField(null=True, default=None)

    class Meta:
        # asset and version-number are unique together
        indexes = ((('asset', 'number'), True),)

    def to_dict(self, recurse=False, backrefs=False, fields=None, exclude=None):
        result = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields, exclude=exclude)
        if self.parent:
            result["parent"] = {"id": self.parent.id, "number": self.parent.number}
        return result

    @classmethod
    def find(cls, project_id: str, name: str) -> AssetVersion:
        """finds the AssetVersion Record from the given asset name

        Parameters
        ----------
        project_id: str
        name: str
                name = asset_class/asset_seq/version_number

        Returns
        -------
            AssetVersion if exists,  None otherwise
        """
        try:
            class_name, seq_id, number = cls.parse_name(name=name)
            # joining multiple tables, peewee documentation
            # https://docs.peewee-orm.com/en/latest/peewee/relationships.html#joining-multiple-tables
            query = AssetVersion.select().join(asset_model.Asset).join(asset_class.AssetClass)
            return query.where(
                (asset_class.AssetClass.project == project_id) &
                (asset_class.AssetClass.name == class_name) &
                (asset_model.Asset.seq_id == seq_id) &
                (AssetVersion.number == number)
            ).get()
        except DoesNotExist:
            return None

    @classmethod
    def find_with_hash(cls,
                       project_id: str,
                       commit_hash: str,
                       class_name: str = None):
        """finds the AssetVersion Record from the given class_name and commit_hash

        Parameters
        ----------
        project_id: str
        class_name: str
                    name of the asset class
        commit_hash: str
              commit hash
        Returns
        -------
            list of Asset Versions
        """
        if not project_id:
            raise Exception("project_id is required")
        if not commit_hash:
            raise Exception("hash can not be null")

        if not class_name:
            query = AssetVersion.select().join(dest=asset_model.Asset).join(asset_class.AssetClass)
            return query.where(
                (AssetVersion.commit_hash == commit_hash) &
                (asset_class.AssetClass.project == project_id)
            )
            # return AssetVersion.select().where(AssetVersion.commit_hash == commit_hash)

        # joining multiple tables, peewee documentation
        # https://docs.peewee-orm.com/en/latest/peewee/relationships.html#joining-multiple-tables
        query = AssetVersion.select().join(dest=asset_model.Asset).join(asset_class.AssetClass)
        return query.where(
            (asset_class.AssetClass.project == project_id) &
            (asset_class.AssetClass.name == class_name) &
            (AssetVersion.commit_hash == commit_hash)
        )

    @classmethod
    def create(cls, user=None, asset=None, objects=None, **query) -> AssetVersion:
        from .version_counter import VersionCounter
        counter: VersionCounter = asset.version_counter.get()
        if not counter:
            raise Exception(f"version_counter record missing for asset:{asset.id}")

        if not objects:
            raise Exception("version can not be created without any objects to commit")

        if "id" in query:
            # pop id if passed by user by mistake, we need this to be auto
            del query["id"]

        if not isinstance(asset, asset_model.Asset):
            # user might have passed id instead of the instance (peewee allows this)
            asset = asset_model.Asset.get(asset_model.Asset.id == asset)

        leaf_version: AssetVersion = counter.leaf_version
        if leaf_version and leaf_version.commit_hash == query["commit_hash"]:
            # same as previous version, it happens mostly when the previous commit was
            # interrupted i.e. server completed commit but client didn't get the data back
            return leaf_version

        object_ids = [object["id"] for object in objects]
        query["asset"] = asset
        query["parent"] = leaf_version
        query["patch"] = cls.compute_diff(from_objects=counter.leaf_objects or [], to_objects=object_ids)
        query["number"] = versioning.increment_version(existing=leaf_version.number if leaf_version else None)
        curr_version: AssetVersion = super(AssetVersion, cls).create(user, **query)
        counter.update_version(user=user,
                               counter=curr_version.number,
                               leaf_version=curr_version,
                               leaf_objects=object_ids
                               )
        return curr_version

    @property
    def is_root(self) -> bool:
        return not self.parent

    def can_add_refs(self) -> bool:
        # only root version can add refs
        return self.is_root

    @property
    def name(self):
        """asset_name/version_number"""
        return f"{self.asset.asset_class.name}/{str(self.asset.seq_id)}/{self.number}"

    @classmethod
    def get_name(cls, asset_name: str, version_number: str):
        if not version_number:
            raise Exception("version_number can not be null")
        return f"{asset_name}/{version_number}"

    @classmethod
    def parse_name(cls, name):
        """return class_name and seq_id from name"""
        if not name:
            raise exceptions.InvalidaAssetNameError("asset name can not be null")
        try:
            parts: list = name.split("/")
            # user can sometimes miss the forward slash while typing
            if len(parts) == 3:
                return parts
            else:
                raise exceptions.InvalidaAssetNameError()
        except ValueError as e:
            raise exceptions.InvalidaAssetNameError(str(e))

    @classmethod
    def compute_patch(cls, version_records, objects):
        """compute add, remove with reference to the latest committed version
        todo: compute patch wrt to leaf_objects in version_counter, instead of
        looping through every foreign-key refernces which is expensive
        """
        prev_objects = set()
        for record in reversed(list(version_records)):
            prev_objects = cls.apply_patch(prev_objects, record.patch)
        return cls.compute_diff(from_objects=prev_objects, to_objects=objects)

    @classmethod
    def compute_diff(cls, from_objects=None, to_objects=None):
        """For diff we only store pointers, this optimizes storage, downloads.
        The added advantage is that:
          - allows us the flexibility of schema modifications in future
          - implement the feature branching and merge should we decide to do so
        """

        from_objects = from_objects or set()
        to_objects = to_objects or set()

        # allow for lists also
        if type(from_objects) is list:
            from_objects = set(from_objects)

        if type(to_objects) is list:
            to_objects = set(to_objects)

        removed = []
        added = []
        for item in from_objects:
            if item not in to_objects:
                removed.append(item)

        for item in to_objects:
            if item not in from_objects:
                added.append(item)

        return {
            "added": added,
            "removed": removed
        }

    @classmethod
    def apply_patch(cls, base: set, patch: dict):
        added = patch["added"]
        removed = patch["removed"]
        # add and remove changes
        for item in added:
            base.add(item)

        for item in removed:
            base.discard(item)
        return base

    def yaml_data(self):
        return {
            "data": self.to_dict(fields=self.__class__.yaml_fields()),
            "url": self.yaml_url
        }

    @property
    def asset_id(self):
        """to avoid loading the full asset object which has db_overhead
        source: https://github.com/coleifer/peewee/issues/609
        """
        return self._data['asset']

    @property
    def yaml_url(self):
        """returns remote url for the asset object"""
        if not self.asset.remote_url or not self.number:
            return None
        return os.path.join(self.asset.remote_url, f"version_{self.number}.yaml")

    @classmethod
    def yaml_fields(cls):
        return [
            "id",
            "number",
            "patch",
            "parent",
            "commit_hash",
            "commit_message",
            "created_by",
            "created_at",
            "size"
        ]

    def write_to_buket(self, storage=None):
        bucket_data = [{"file": InMemoryFile(file_ext=".yaml", file_data=self.to_dict()),
                        "url": self.yaml_url}]
        storage = storage or StorageFactory.storage_for_url(src_url=self.yaml_url)
        transporter: Transporter = storage.get_transporter()
        transporter.write_to_bucket(data=bucket_data)
