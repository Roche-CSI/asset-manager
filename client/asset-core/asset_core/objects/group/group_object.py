from __future__ import annotations

import json
import os
from typing import Callable, List

from asset_contents.content import Content
from asset_core.objects.group.member_object import GroupMemberObject
from asset_core.objects.object import Object
from asset_core.objects.object_source import ObjectSource
from asset_utils.common import exceptions
from asset_utils.utils.file_utils import FileUtils

RAW_FILE_PATH = ".asset/.raw/{filename}.zip"  # this is where we store the raw form of the group-object


class GroupObject(Object):
    """GroupObject class that combined multiple objects and contents into a single group.
    The key difference here is that it can combine large number of files into a single group
    which greatly enhances the efficiency when handling when dealing with thousands or millions of files.

    We do the following when you are adding large files into a group
    - create separate objects from each source
    - serialize and write all objects to a json file, we choose json because its much faster to read and write as compared to yaml
    - the filename would be <meta-hash>.json
    - save the file inside .assets/.raw directory - create the directory if not exists
    - add that file as an object
    """
    object_type: str = "group"
    members: list = []

    @classmethod
    def bulk_create(cls,
                    factory,
                    sources: [ObjectSource],
                    callback: Callable = None,
                    repo_dir: str = None) -> [Object]:
        if not sources:
            return []

        src, members = cls._create_as_raw(factory=factory, sources=sources, callback=callback, repo_dir=repo_dir)
        obj = super(GroupObject, cls).create(content=src.content, path=src.path_in_asset, callback=None)
        obj.members = members
        return [obj]

    @classmethod
    def _create_as_raw(cls, factory, sources, callback: Callable = None, repo_dir: str = None):
        members = []
        for object_src in sources:
            obj = GroupMemberObject.create(content=object_src.content, path=object_src.path_in_asset)
            members.append(obj)
            if callback:
                callback(obj)
        return cls._get_raw_object_source(factory=factory, members=members, repo_dir=repo_dir), members

    @classmethod
    def _get_raw_object_source(cls, factory, members: [GroupMemberObject], repo_dir: str = None) -> ObjectSource:
        # create individual objects
        member_ids = [member.id for member in members]
        filename = FileUtils.string_md5(",".join(sorted(member_ids)))  # sort it to ignore ordering
        path = RAW_FILE_PATH.format(filename=filename)

        serialized = {member.id: member.serialize() for member in members}
        json_string = json.dumps(serialized, indent=4, sort_keys=True, default=str)
        # write to raw objects path
        object_path = os.path.join(repo_dir, path)
        FileUtils.write_file(abs_path=object_path, content=json_string, compressed=True)
        # add that file as a regular object
        sources = factory.parse_sources(repo_dir=repo_dir, targets=[object_path])
        object_sources: ObjectSource = factory.create_contents(source_data=sources, proxy=False)
        return object_sources[0]

    @classmethod
    def create(cls,
               content: Content,
               path: str,
               callback: Callable = None,
               proxy: bool = False
               ) -> GroupObject:
        raise exceptions.AssetException("GroupObject can only be created using bulk_create")

    def can_update(self):
        return False

    def add_to_asset(self, asset, **kwargs):
        if not self.members:
            raise exceptions.AssetException("invalid group object, there are no members")

        super().add_to_asset(asset=asset, **kwargs)
        # add the members to content
        for member in self.members:
            member.add_to_asset(asset=asset)

    def link_to_store(self, callback: Callable = None, save: bool = False):
        for obj in self.members:
            # deactivate saving here, we will save all objects at once
            obj.link_to_store(save=False)
            if callback:
                callback(obj)
        super().link_to_store(save=save)

    def link_from_store(self, callback: Callable = None, save: bool = False) -> bool:
        for obj in self.members:
            # deactivate saving here, we will save all objects at once
            obj.link_from_store(save=False)
            if callback:
                callback(obj)
        return super().link_from_store(save=save)

    @classmethod
    def serialize_fields(cls):
        return [*super(GroupObject, cls).serialize_fields(), "object_type"]

    @classmethod
    def de_serialize(cls, asset, data: dict) -> GroupObject:
        if asset.view == cls.views.RAW:
            # only the raw object here, don't deserialize members in raw mode
            obj: GroupObject = super(GroupObject, cls).de_serialize(asset=asset, data=data)
        elif asset.view == cls.views.DATA:
            # don't add the raw object to asset if in data mode
            obj: GroupObject = cls.from_dict(asset=asset, data=data)
            # data mode
            obj.members = obj.deserialize_members()
        else:
            raise NotImplementedError()

        return obj

    @property
    def has_raw_mode(self):
        return True

    def deserialize_members(self):
        members = self.load_members()
        for member in members:
            member.parent_obj = self
            member.update_asset()

        return members

    def load_members(self) -> List[GroupMemberObject]:
        raw_data = self._read_raw_file()
        filename, ext = os.path.splitext(os.path.basename(self.path))
        member_data: dict = json.loads(raw_data[filename])
        return list(map(lambda x: GroupMemberObject.from_dict(asset=self.asset, data=x), member_data.values()))

    def _read_raw_file(self) -> dict:
        if not os.path.exists(self.content.cache_path):
            raise exceptions.AssetException(f"raw file not found for group_object:{self.path}")
        return FileUtils.read_file(filepath=self.content.cache_path, compressed=True)
