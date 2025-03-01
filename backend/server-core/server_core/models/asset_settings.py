from __future__ import annotations
from peewee import *
from .base.base import db_proxy as db
from .base.read_write import ReadWriteModel


class AssetSettings(ReadWriteModel):
    name = CharField(null=False)
    description = TextField(null=True)  # optional
    value = TextField(null=False)

    class Meta:
        indexes = ((('name',), True),)

    @classmethod
    def create(cls, user: str =None, **query) -> AssetSettings:
        with db.atomic() as txn:
            return super(AssetSettings, cls).create(user, **query)

    @property
    def yaml_url(self):
        pass

    @classmethod
    def yaml_fields(cls):
        pass

    @classmethod
    def default_project(cls):
        record = cls.get_if_exists(cls.name == 'default_project')
        if not record:
            return None
        from .project import Project
        project = Project.get_if_exists(Project.name == record.value)
        return project

    @classmethod
    def supported_cli_version(cls):
        record = cls.get_if_exists(cls.name == 'min_cli_version')
        return record.value if record else None

    @classmethod
    def server_available(cls):
        record = cls.get_if_exists(cls.name == 'server_available')
        return str(record.value).lower() == "true" if record else False

