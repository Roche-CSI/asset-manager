from typing import Iterable
from .base.read_only import ReadOnlyModel
from peewee import ForeignKeyField, BigAutoField, BooleanField
from .asset import Asset
from .object import Object, Content


class AssetObjectRelations(ReadOnlyModel):
    """Join table for asset-object relations
    """
    id = BigAutoField(primary_key=True)
    asset = ForeignKeyField(Asset, backref="object_joins", null=False, on_delete='CASCADE')
    object = ForeignKeyField(Object, backref="asset_joins", null=False, on_delete='CASCADE')
    saved_to_bucket = BooleanField(null=False, default=False)

    class Meta:
        indexes = ((('asset', 'object'), True),)

    def to_dict(self, recurse=False, backrefs=False, fields=None):
        return super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields, exclude={AssetObjectRelations.asset})

    @classmethod
    def get_objects_not_saved_to_bucket(cls, asset_id):
        # https://docs.peewee-orm.com/en/latest/peewee/relationships.html
        query = cls.select() \
            .join(Object, on=(AssetObjectRelations.object == Object.id)) \
            .join(Content, on=(Object.content == Content.id)) \
            .where((cls.asset == asset_id) & (cls.saved_to_bucket == False))
        return list(map(lambda x: x, query.dicts()))

    @classmethod
    def update_saved_to_bucket(cls, record_ids: Iterable[str], value: bool):
        if not record_ids:
            return
        query = cls.update(saved_to_bucket=value).where(cls.id.in_(record_ids))
        query.execute()
