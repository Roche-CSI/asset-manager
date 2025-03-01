from peewee import *
from playhouse.postgres_ext import JSONField
from .base.read_write import ReadWriteModel
from .asset import Asset
from .asset_version import AssetVersion


class VersionCounter(ReadWriteModel):
    id = AutoField(primary_key=True)
    # one to one relationship here
    asset = ForeignKeyField(Asset, backref='version_counter', null=False, on_delete='CASCADE', unique=True)
    counter = CharField(default=None, null=True)
    root_version = ForeignKeyField(AssetVersion, backref='root', null=True, on_delete='SET NULL')  # root version
    leaf_version = ForeignKeyField(AssetVersion, backref='leaf', null=True, on_delete='SET NULL')  # latest committed version
    # possible to remove all objects in which case leaf node will not have any
    leaf_objects = JSONField(default=list, null=True)

    def update_version(self, user, counter, leaf_version, leaf_objects):
        self.leaf_objects = self.validate_objects(leaf_objects)
        # increment the counter
        self.counter = counter
        # switch leaf node pointer
        self.leaf_version = leaf_version
        fields = [
            VersionCounter.leaf_objects,
            VersionCounter.counter,
            VersionCounter.leaf_version
        ]
        if not self.root_version:
            self.root_version = leaf_version  # first commit
            fields.append(VersionCounter.root_version)

        self.save(user=user, only=fields)

    def validate_objects(self, objects):
        """We only store a list of strings, so we raise error if user
        passed the full objects
        """
        result = []
        for object in objects:
            if type(object) is not str:
                raise Exception(f"received in valid type:{type(object)} instead of str")
            result.append(object)
        return result

