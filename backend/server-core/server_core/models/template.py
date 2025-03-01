from peewee import *
from playhouse.postgres_ext import JSONField
from server_core.models.base.read_write import ReadWriteModel


class Template(ReadWriteModel):
    name = CharField(unique=True)
    title = CharField(null=True)
    version = CharField(null=True)
    description = TextField(null=True)
    category = CharField(null=True)  # asset, object, etc
    readme = TextField(null=True)
    is_active = BooleanField(null=False, default=True)
    sample_data = JSONField(null=True, default=dict)
    configs = JSONField(null=True, default=dict)

    class Meta:
        indexes = (
            (('name', 'version'), True),
        )

