from __future__ import annotations
from peewee import *
from .base.read_write import ReadWriteModel


class AppSecret(ReadWriteModel):
    name = CharField(null=False)
    secret = TextField(null=True, default='n/a')
    is_active = BooleanField(null=False, default=True)

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()





