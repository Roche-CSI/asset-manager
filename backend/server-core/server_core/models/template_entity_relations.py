from peewee import *
from playhouse.postgres_ext import JSONField
from server_core.models.base.read_write import ReadWriteModel
from server_core.models.template import Template


class TemplateEntityRelations(ReadWriteModel):
    template = ForeignKeyField(Template, backref='template_entity_relations', on_delete='CASCADE', null=False)
    entity_type = CharField(null=True)  # asset_class, asset, object, etc
    entity_id = CharField(null=True)  # asset_class_id, asset_id, object_id, etc
    is_active = BooleanField(null=False, default=True)
    configs = JSONField(null=True, default=dict)  # pattern to decide where template is applied

    class Meta:
        indexes = (
            (('template', 'entity_type', 'entity_id'), True),
        )
