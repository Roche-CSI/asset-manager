from __future__ import annotations
from peewee import *
from playhouse.postgres_ext import JSONField
from server_core.models.base import read_only
from server_core.models import asset_version
from server_core.asset_client import exceptions

DEFAULT_LABEL = 'n/a'


class AssetRef(read_only.ReadOnlyModel):
    id = BigAutoField(primary_key=True)
    src_version = ForeignKeyField(asset_version.AssetVersion,
                                  backref='dependents',
                                  on_delete='CASCADE')  # child assets
    dst_version = ForeignKeyField(asset_version.AssetVersion,
                                  backref='depends_on',
                                  on_delete='CASCADE')  # parent assets
    # label can;t be null since we are indexing it, we need a default here
    label = TextField(null=False, default=DEFAULT_LABEL)
    # using name properties instead of property to avoid conflict with python default
    properties = JSONField(default=None, null=True)

    class Meta:
        indexes = ((('src_version', 'dst_version', 'label'), True),)

    @classmethod
    def create_if_not_exists(cls,
                             user: str,
                             src_version: int,
                             dst_version: int,
                             label: str,
                             properties: dict) -> AssetRef:
        """AssetRef record is a link between two different assets i.e. asset + version
        since the Version table captures the asset-state and has a foreign key to Asset table.
        Here we just maintain the ForeignKey to Version table.

        Parameters
        ----------
        user: str
            user id
        src_version: int
            record id of source version
        dst_version: int
            record id of dest version
        label: str
            ref label, todo: enforce label choices
        properties: dict
            properties for the ref

        Returns
        -------
        """
        label = label or DEFAULT_LABEL
        # if record exists with the same label, we don't create again
        record = cls.get_if_exists(AssetRef.src_version == src_version,
                                   AssetRef.dst_version == dst_version,
                                   AssetRef.label == label,
                                   include_deleted_records=True
                                   )
        if record:
            if record.is_deleted:
                # restore if soft deleted earlier
                record.restore()
        else:
            if src_version == dst_version:
                raise exceptions.ForbiddenRefError(msg="asset can not reference itself")
            record = cls.create(user=user,
                                src_version=src_version,
                                dst_version=dst_version,
                                label=label,
                                properties=properties
                                )
        return record

    def to_dict(self, recurse=False, backrefs=False, fields=None):
        result = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields)
        result['src_version'] = self.version_data(self.src_version)
        result['dst_version'] = self.version_data(self.dst_version)
        # result['src_version'] = {'name': self.src_version.name, 'id': self.src_version.id}
        # result['dst_version'] = {'name': self.dst_version.name, 'id': self.dst_version.id}
        return result

    def version_data(self, version: asset_version.AssetVersion):
        return {
            'name': version.name,
            'id': version.id,
            'asset': version.asset.id,
            'asset_class': version.asset.asset_class.id
        }

    @classmethod
    def find(cls, project_id: str, name: str, instance=None) -> dict:
        """Finds all refs for an Asset.

        Parameters
        ----------
        project_id : str
            The project id.
        name : str
            The name of the asset. It follows the format: asset_class/asset_seq/version_number.
        instance : AssetVersion, optional
            An instance of the AssetVersion class, by default None.

        Returns
        -------
        dict
            A dictionary containing the dependents and depends_on lists for the asset.
            Format: {dependents: [], depends_on: []}
        """
        if not project_id:
            raise Exception("project_id is required")
        result = {}
        version = instance or asset_version.AssetVersion.find(project_id=project_id, name=name)
        if not version:
            result["error"] = "asset not found:{}".format(name)
            return result

        result['dependents'] = [ref.to_dict() for ref in version.dependents if not ref.is_deleted]
        result['depends_on'] = [ref.to_dict() for ref in version.depends_on if not ref.is_deleted]
        return result
