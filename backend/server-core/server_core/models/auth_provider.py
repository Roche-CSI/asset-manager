from __future__ import annotations
from peewee import *
from playhouse.postgres_ext import JSONField
from .base.read_write import ReadWriteModel


class AuthProvider(ReadWriteModel):
    name = CharField(null=False)
    description = TextField(null=True, default='n/a')
    is_active = BooleanField(null=False, default=True)
    configs = JSONField(default=dict, null=True)

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()



