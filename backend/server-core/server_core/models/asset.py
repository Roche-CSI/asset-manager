from __future__ import annotations

import json
import os
from functools import reduce
from typing import Dict, Any, Optional

from asset_pluggy.storage.storage_factory import StorageFactory
from asset_pluggy.storage.transporter import Transporter
from asset_utils.utils.in_memory_file import InMemoryFile
from peewee import *
from peewee import operator
from playhouse.postgres_ext import JSONField

from server_core.asset_client.exceptions import AssetException
from server_core.utils.query_paginator import Paginator
from .asset_class import AssetClass
from .base.base import db_proxy as db
from .base.read_write import ReadWriteModel

ALIAS_YAML_FILE_NAME_FORMAT = "{id}__{seq_id}__{alias}.yaml"


class PhaseEnums:
    NOT_APPLICABLE = 0
    DRAFT = 1
    EXPERIMENTAL = 2,
    BETA = 3,
    RELEASED = 4,
    STABLE = 5


PHASE_CHOICE = (
    (PhaseEnums.NOT_APPLICABLE, 'Not-Applicable'),
    (PhaseEnums.DRAFT, 'Draft'),
    (PhaseEnums.EXPERIMENTAL, 'Experimental'),
    (PhaseEnums.BETA, 'Beta'),
    (PhaseEnums.RELEASED, 'Released'),
    (PhaseEnums.STABLE, 'Stable'),
)


class Asset(ReadWriteModel):
    asset_class = ForeignKeyField(AssetClass, backref='assets', null=False, on_delete='CASCADE')
    seq_id = IntegerField(null=False, default=1)
    owner = CharField(null=False)  # owner and created_by can be different if the employee leaves org
    top_hash = CharField(null=True)  # all versions of an asset share the top hash
    alias = TextField(null=True)  # user defined name for a node
    frozen = BooleanField(null=False, default=False)
    # added for better user experience
    title = CharField(null=True)
    description = TextField(null=True)
    attributes = JSONField(null=True, default=dict)
    metadata = JSONField(null=True, default=dict)
    phase = IntegerField(choices=PHASE_CHOICE, default=0)

    class Meta:
        indexes = (
            (('asset_class', 'seq_id'), True),
            (('asset_class', 'alias'), True),
        )

    @classmethod
    def create(cls, asset_class, seq_id=None, user=None, **query):
        with db.atomic() as txn:
            query["owner"] = query.get("owner", user)
            # if there are no sequence ids or invalid seq_id i.e. temp_1639697172 then it's a root node
            # if there is a already a sequence id then its a leaf node i.e. version
            if not seq_id or not str(seq_id).isnumeric():
                # asset_class = query.get("asset_class")
                if not asset_class:
                    raise Exception("missing required parameter: asset_class")
                if not isinstance(asset_class, AssetClass):
                    # user might have passed id instead of the instance (peewee allows this)
                    asset_class = AssetClass.get(AssetClass.id == asset_class)
                seq_id = asset_class.increment_asset_seq(user=user)

            query["seq_id"] = seq_id
            query["asset_class"] = asset_class
            query["top_hash"] = str(asset_class.id)
            asset: Asset = super(Asset, cls).create(user, **query)
            asset.create_version_counter(user=user)
            asset.did_create = True
            # create input pointers
            # _ = asset.add_refs_pointer(user=user)
            return asset

    def to_dict(self, recurse=False, backrefs=False, fields=None):
        # correct for incorrect string metadata
        if self.metadata and isinstance(self.metadata, str):
            self.metadata = self.parse_metadata_string(self.metadata)
            fields

        data = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields)
        if recurse:
            # add version informations
            data["versions"] = [version.to_dict() for version in self.get_versions()]
        return data

    def save(self, user=None, force_insert=False, only=None):
        # if metadata is string, convert it to dict
        # happens sometimes from the javascript client side if the user is not careful
        if isinstance(self.metadata, str):
            self.metadata = self.parse_metadata_string(self.metadata)
            if only and Asset.metadata not in only:
                only.append(Asset.metadata)
        return super().save(user=user, force_insert=force_insert, only=only)

    @staticmethod
    def parse_metadata_string(json_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse a potentially malformed JSON string into a dictionary.

        Args:
            json_str: The JSON string to parse

        Returns:
            Dict containing the parsed metadata, or None if parsing fails
        """
        try:
            # First try: direct parsing
            data = json.loads(json_str)
            if isinstance(data, str):
                data = json.loads(data)
                if isinstance(data, str):
                    raise json.JSONDecodeError
                return data
        except json.JSONDecodeError:
            try:
                # Second try: clean the string
                # Remove any leading/trailing whitespace
                clean_str = json_str.strip()

                # If the string starts with single quotes, replace with double quotes
                if clean_str.startswith("'") and clean_str.endswith("'"):
                    clean_str = clean_str[1:-1]

                # Escape any unescaped double quotes
                clean_str = clean_str.replace('\\"', '"').replace('"', '\\"')

                # Add quotes if they're missing
                if not clean_str.startswith('"'):
                    clean_str = f'"{clean_str}"'

                # Parse the cleaned string
                return json.loads(clean_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                raise

    def create_version_counter(self, user):
        """Local import to avoid circular"""
        from .version_counter import VersionCounter
        return VersionCounter.create(user=user, asset=self)

    @property
    def name(self):
        """asset_class_name/seq_id"""
        return f"{self.asset_class.name}/{str(self.seq_id)}"

    @property
    def did_create(self) -> bool:
        try:
            return self._did_create
        except AttributeError:
            self._did_create = False
            return self._did_create

    @did_create.setter
    def did_create(self, x: bool):
        self._did_create = x

    def get_versions(self, committed=None):
        """get all version of an asset
        committed: bool
            can be True, False or None, None means ignore
        """
        from .asset_version import AssetVersion
        if committed is None:
            query = self.versions  # ModelSelect is a wrapper around query
        else:
            query = self.versions.where(AssetVersion.commit_hash.is_null(not committed))

        return query.order_by(AssetVersion.created_at.desc())

    def root_version(self):
        return self.version_counter.get().root_version

    def leaf_version(self):
        return self.version_counter.get().leaf_version

    def all_objects(self):
        """returns all objects for the asset"""
        from server_core.models.asset_object_relations import AssetObjectRelations
        from server_core.models.object import Object
        query = Object \
            .select() \
            .join(AssetObjectRelations, on=(Object.id == AssetObjectRelations.object)) \
            .where(AssetObjectRelations.asset == self.id)
        return query.execute()

    @classmethod
    def list_assets(cls, class_id: str, ids_only: bool = False, recurse: bool = False,
                    seq_id: int = None, owner: str = None, alias: str = None, search_by: str = None,
                    page_number: int = None, page_size: int = None):
        from .version_counter import VersionCounter
        from .asset_version import AssetVersion
        query = Asset.select(Asset.id) if ids_only else Asset.select()
        query = query.where(Asset.asset_class == class_id).order_by(Asset.seq_id.desc())
        query = cls._append_list_asset_conditions(query=query, seq_id=seq_id, owner=owner, alias=alias,
                                                  search_by=search_by)
        query, page_count = Paginator.paginate(query, page_number, page_size)
        if recurse:
            query \
                .join(AssetClass, on=(Asset.asset_class == AssetClass.id)) \
                .join(VersionCounter, on=(VersionCounter.asset == Asset.id)) \
                .join(AssetVersion, on=VersionCounter.leaf_version == AssetVersion.id)
        data = query.execute()
        return data, page_count

    @classmethod
    def find(cls, seq_id, project_id=None, class_name=None, class_id=None):
        if not seq_id:
            raise Exception("missing required parameter: seq_id")
        if not class_id:
            asset_class = AssetClass.get(AssetClass.project_id == project_id, AssetClass.name == class_name)
            class_id = str(asset_class.id)
        return cls.get_if_exists(cls.asset_class_id == class_id, cls.seq_id == seq_id)

    @staticmethod
    def _append_list_asset_conditions(query, seq_id, owner, alias, search_by):
        if seq_id or owner or alias:
            conditions = list()
            conditions.append(Asset.seq_id.cast('text') == seq_id) if seq_id else None
            conditions.append(Asset.owner == owner) if owner else None
            conditions.append(Asset.alias == alias) if alias else None
            condition = reduce(operator.and_, conditions)
            query = query.where(condition)
        elif search_by:
            query = query.where(
                (Asset.alias.contains(search_by)) |
                (Asset.owner.contains(search_by)) |
                (Asset.seq_id.cast('text') == search_by)
            )
        return query

    @property
    def asset_class_id(self):
        """to avoid loading the full asset-class object which has db_overhead
        source: https://github.com/coleifer/peewee/issues/609
        """
        return self._data['asset_class']

    @property
    def remote_url(self):
        if not self.seq_id:
            return None
        return os.path.join(self.configs.assets_url, str(self.asset_class.id), str(self.seq_id))

    @property
    def alias_dir_url(self):
        if not self.seq_id or not self.id:
            return None
        return os.path.join(self.configs.aliases_url, str(self.asset_class.id))

    @property
    def alias_yaml_url(self):
        if not self.seq_id or not self.seq_id or not self.alias:
            return None
        filename = ALIAS_YAML_FILE_NAME_FORMAT.format(id=str(self.id), seq_id=self.seq_id, alias=self.alias)
        return os.path.join(self.alias_dir_url, filename)

    @property
    def yaml_url(self):
        if not self.seq_id or self.seq_id is None:
            raise AssetException("Invalid asset , missing seq_id")
        return os.path.join(self.remote_url, "asset.yaml")

    def write_to_bucket(self, alias=False):
        with self.asset_class.project.storage():
            asset_data = self.to_dict()
            asset_file = InMemoryFile(file_ext=".yaml", file_data=asset_data)
            bucket_data = [{"file": asset_file, "url": self.yaml_url}]
            # only write alias file if alias is set
            if alias and self.alias:
                bucket_data.append({"file": asset_file, "url": self.alias_yaml_url})

            storage = StorageFactory.storage_for_url(src_url=self.yaml_url)
            transporter: Transporter = storage.get_transporter()
            transporter.write_to_bucket(data=bucket_data)
            if alias:
                self._alias_cleanup(storage)
            return self.yaml_url

    def _alias_cleanup(self, storage):
        """Cleanup any old alias files while updating the alias."""
        blob_pattern = ALIAS_YAML_FILE_NAME_FORMAT.format(id=str(self.id), seq_id=str(self.seq_id), alias="*")
        blobs = storage.list_blobs(url=os.path.join(self.alias_dir_url, blob_pattern))
        if not blobs:
            # no alias files found, nothing to delete
            return
        if len(blobs) == 1:
            if not self.alias:
                # removing the alias, delete the old alias file
                storage.delete_blobs([blobs[0].url])
            return
        if len(blobs) > 2:
            # there should never be more than 2 aliases, since we clean up after every update
            raise AssetException("Invalid number of alias files found")

        old_aliases = []
        current_alias = ALIAS_YAML_FILE_NAME_FORMAT.format(id=str(self.id), seq_id=str(self.seq_id), alias=self.alias)
        for blob in blobs:
            if os.path.basename(blob.name) != current_alias:
                old_aliases.append(blob.url)
        # delete the old alias file
        storage.delete_blobs(old_aliases)

    @classmethod
    def yaml_fields(cls):
        return [
            "id",
            "asset_class",
            "seq_id",
            "alias",
            "tags",
            "top_hash",
            "frozen",
            "created_at",
            "created_by",
            "owner",
            "modified_at",
            "modified_by",
            "title",
            "description",
            "attributes",
            "metadata",
            "tags",
            "phase"
        ]

    @classmethod
    def find_by_name(cls, asset_name: str) -> Asset:
        class_name, seq_id = asset_name.split("/")
        class_id = AssetClass.get_if_exists(AssetClass.name == class_name)
        if class_id:
            return cls.get_if_exists(cls.asset_class == class_id, cls.seq_id == seq_id)
        return None
