from __future__ import annotations
import os
from server_core.utils.file_utils import FileUtils
from .base.read_only import ReadOnlyModel
from peewee import TextField, ForeignKeyField, CharField, DoesNotExist, BigIntegerField
from playhouse.postgres_ext import JSONField
from .content import Content


class Object(ReadOnlyModel):
    """AssetObject to Asset is a many to many
    So we use a join table
    Asset -> Join table is one to many
    AssetObject to Join table is one to many

    """
    id = CharField(primary_key=True, unique=True)  # content_id::path
    url_id = CharField(null=False)
    object_type = CharField(null=True)
    content = ForeignKeyField(Content, backref='objects', on_delete='CASCADE', null=False)  # urlsafeencode of md5
    meta = JSONField(null=True, default=dict)  # any meta information
    size = BigIntegerField(null=True)  # size of the object

    # class Meta:
    # #     # non unique indexing, because of hash collision possibility
    # #     indexes = ((('content_id'), False),)

    @classmethod
    def get(cls, *query, **filters) -> Object:
        try:
            return super(Object, cls).get(*query, **filters)
        except DoesNotExist as e:
            cls.logger().info(e)
            return None

    @classmethod
    def create(cls, user=None, **query):
        if not query.get("id", None):
            raise Exception("missing required parameter id")
        query["url_id"] = cls.compute_url_id(object_id=query["id"])
        created = super(Object, cls).create(user=user, **query)
        # the sequence field doesn't get updated until its written to db
        # so we need to read again to make sure we get the sequence field updated
        return cls.get(cls.id == created.id)

    @property
    def yaml_path(self):
        return os.path.join("objects", f"{self.url_id}.yaml")

    @classmethod
    def objects_url(cls, asset_url: str, version: str, commit_hash: str):
        # note: v2: we are storing as compressed json files, max one write for each version commit
        return os.path.join(asset_url, "objects_v2", f"{version}_{commit_hash}.zip")

    # def to_dict(self, recurse=False, backrefs=False, fields=None):
    #     result = super(Object, self).to_dict(recurse=False, backrefs=backrefs, fields=fields)
    #     if recurse:
    #         if 'content' in result:
    #             result['content'] = self.content.to_dict(fields=Content.yaml_fields())
    #     return result

    @classmethod
    def last_record(cls):
        try:
            return Object.select().order_by(Object.url_id.desc()).get()
        except DoesNotExist:
            return None

    @classmethod
    def yaml_fields(cls):
        return [
            "id",
            "created_by",
            "created_at",
            "content",
            "object_type",
            "size"
        ]

    @classmethod
    def batch_insert(cls, user: str, data: list) -> list:
        for item in data:
            item["url_id"] = cls.compute_url_id(object_id=item["id"])
        return super(Object, cls).batch_insert(user=user, data=data)

    @classmethod
    def compute_url_id(cls, object_id: str):
        return FileUtils.url_safe_md5(FileUtils.string_md5(object_id, b64=True))

    @classmethod
    def batch_read(cls, ids: list) -> list:
        objects_data = super(Object, cls).batch_read(ids=ids)
        if not objects_data:
            return []
        # get contents
        # https://github.com/coleifer/peewee/issues/1177
        # note: this is much faster than join query + to_dict()
        contents = Content.batch_read(ids=list(map(lambda x: x.get("content"), objects_data)))
        # transform to dict, we need to assign to objects
        content_dict = {content["id"]: content for content in contents}
        for obj in objects_data:
            obj["content"] = content_dict[obj["content"]]
        return objects_data
