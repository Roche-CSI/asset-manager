from __future__ import annotations
from peewee import *
from playhouse.postgres_ext import JSONField
from .base.read_write import ReadWriteModel


class User(ReadWriteModel):
    username = CharField(null=False)
    email = CharField(null=False)
    is_active = BooleanField(null=False, default=True)
    g_info = JSONField(default={})  # info returned by google
    token = TextField(default=None, null=True)
    is_admin = BooleanField(null=False, default=False)

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()

    def get_roles(self, credentials=True):
        result = []
        project_fields = ["id", "name", "title", "description", "is_active", "staging_url", "remote_url", "status"]
        if credentials:
            project_fields.extend(["credentials_user", "storage_token"])
        for user_role in self.roles:
            data = user_role.role.to_dict()
            data["project"] = user_role.role.get_project().to_dict(fields=project_fields)
            result.append(data)
        return result

    # Flask-Login integration for admin interface
    @property
    def is_authenticated(self):
        # user is authenticated for admin interface if they are project admin
        if hasattr(self, "is_admin") and self.is_admin:
            return True
        return False

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
