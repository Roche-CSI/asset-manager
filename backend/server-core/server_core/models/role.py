"""temporary workaround before we implement a full ABAC"""

from __future__ import annotations
from peewee import *
from .base.read_write import ReadWriteModel


class Role(ReadWriteModel):
    id = AutoField(primary_key=True)
    name = CharField(null=False)
    project_name = CharField(null=False)
    can_read = BooleanField(null=False, default=True)
    can_edit = BooleanField(null=False, default=False)
    can_delete = BooleanField(null=False, default=False)
    can_admin_project = BooleanField(null=False, default=False)

    def get_project(self):
        from .project import Project
        return Project.get_if_exists(Project.name == self.project_name)

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @property
    def yaml_fields(cls):
        raise NotImplementedError()

    @classmethod
    def create_if_not_exists_for_project(
            cls, project_name: str, username: str = None, can_admin_project: bool = False):
        role_record = cls.get_if_exists(cls.project_name == project_name,
                                        cls.can_admin_project == can_admin_project)
        print(f'role_record: {role_record}')
        if not role_record:
            # create
            if can_admin_project:
                role_record = cls.create(user=username,
                                         name=f'edit_{project_name}_admin',
                                         project_name=project_name,
                                         can_read=True,
                                         can_edit=True,
                                         can_delete=False,
                                         can_admin_project=True
                                         )
            else:
                role_record = cls.create(user=username,
                                         name=f'edit_{project_name}_user',
                                         project_name=project_name,
                                         can_read=True,
                                         can_edit=True,
                                         can_delete=False,
                                         can_admin_project=False
                                         )
        return role_record
