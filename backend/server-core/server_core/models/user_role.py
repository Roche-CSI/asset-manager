"""temporary workaround before we implement a full ABAC"""

from __future__ import annotations
from peewee import *
from .base.read_write import ReadWriteModel
from .user import User
from .role import Role


class UserRole(ReadWriteModel):
    id = AutoField(primary_key=True)
    asset_user = ForeignKeyField(User, backref='roles', on_delete='CASCADE', null=False)
    role = ForeignKeyField(Role, backref='users', on_delete='CASCADE', null=False)

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()

    @classmethod
    def create_if_not_exists_for_role(cls, role_id: str, user_id: str, username: str):
        # check if roles exist for default project
        # link user to role for the default project, check in deleted records also
        user_role = UserRole.get_if_exists(UserRole.role == role_id,
                                           UserRole.asset_user == user_id,
                                           include_deleted_records=True)
        if not user_role:
            user_role = UserRole.create(user=username,
                                        role=role_id,
                                        asset_user=user_id)

        if user_role.is_deleted:
            user_role.is_deleted = False
            user_role.save(user=username, only=[UserRole.is_deleted])

        return user_role

    @classmethod
    def create_by_role_id_username(cls, role_id, username):
        """Create user role using role_id and username"""
        current_user: User = User.get_if_exists(User.username == username)
        if not current_user:
            current_user = User.create(user=username)
        new_user_role: UserRole = UserRole.create_if_not_exists_for_role(
            role_id=role_id,
            user_id=current_user.id,
            username=username)
        return new_user_role

    def to_dict(self, recurse=False, backrefs=False, fields=None, exclude=None):
        result = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields, exclude=exclude)
        return result
