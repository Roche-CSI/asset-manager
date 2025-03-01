"""Asset-Class and Content are many-many relations.
The blob store for content is name-spaced to asset-class i.e.
the same content can be stored in two different asset-class directories inside
the bucket, i.e. a content can point to multiple different asset-classes.

On the other hand, an asset-class will obviously have multiple contents

The asset_class_content_relations table captures this relationship
"""

from peewee import *
from .asset_class import AssetClass
from .content import Content
from .base.read_only import ReadOnlyModel


class AssetClassContentRelations(ReadOnlyModel):

    id = BigAutoField(primary_key=True)
    asset_class = ForeignKeyField(AssetClass, backref="content_joins", null=False, on_delete='CASCADE')
    content = ForeignKeyField(Content, backref="asset_class_joins", null=False, on_delete='CASCADE')

    class Meta:
        indexes = ((('asset_class', 'content'), True),)
