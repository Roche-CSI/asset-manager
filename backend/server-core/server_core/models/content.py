from __future__ import annotations
import os
from .base.read_only import ReadOnlyModel
from peewee import *
from playhouse.postgres_ext import JSONField
from server_core.configs import Configs
from server_core.utils.file_utils import FileUtils

HASH_SEP = "_"
ID_SEP = ":"


class Content(ReadOnlyModel):
    id = CharField(primary_key=True, unique=True)  # gs$<hash>, bq$<hash> etc
    mime_type = CharField(null=True)  # mime type
    hash = CharField(null=False)  # storing hash separately for better indexing
    # file size in bytes, we store it here since all content won't be stored in buckets
    size = BigIntegerField(null=True)
    meta = JSONField(default=dict, null=True)

    class Meta:
        # non unique indexing here
        # same data can exist in 2 different storage systems i.e. gs and bq
        indexes = ((('hash',), False),)

    @classmethod
    def yaml_fields(cls) -> list:
        return [
            "id",
            "hash",
            "mime_type",
            "size",
            "meta",
            "created_by",
            "created_at"
        ]

    def can_download(self):
        if not self.is_proxy:
            return True
        src = (self.meta or {}).get("src") or None
        # todo: this is adhoc, we need a protocol for this
        return src != "gcr"

    @property
    def is_proxy(self):
        return bool((self.meta or {}).get("proxy"))

    def read_url(self, class_id: str):
        """read url for content"""
        if self.is_proxy:
            return self.meta["src"]
        return os.path.join(Configs.shared().contents_url(staging=False), class_id, self.file_id)

    @property
    def file_id(self):
        return FileUtils.url_safe_md5(b64_md5=self.hash_value)

    @property
    def hash_type(self):
        return Content.parse_hash(str(self.hash))[0]

    @property
    def hash_value(self):
        return Content.parse_hash(str(self.hash))[1]

    @classmethod
    def parse_id(cls, id: str) -> list:
        """returns a tuple of storage_id and hash"""
        return id.split(ID_SEP)

    @classmethod
    def parse_hash(cls, hash) -> list:
        """returns a tuple of hash_type and hash_value"""
        return hash.split(HASH_SEP)