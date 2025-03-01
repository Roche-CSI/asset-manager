from asset_utils.utils.file_utils import FileUtils
from peewee import *
from playhouse.postgres_ext import JSONField

from .base.read_write import ReadWriteModel


class TagQueries(ReadWriteModel):
    tag_hash = CharField(null=False)
    table_name = CharField(null=False)
    record_id = CharField(null=False)
    result = JSONField(default=dict, null=False)

    QUERY_PRIORITY = {
        "asset_version": 10,
        "asset": 9,
        "asset_class": 8,
    }

    class Meta:
        indexes = ((('tag_hash', 'table_name', 'record_id'), True),)

    @classmethod
    def create_if_not_exists(cls,
                             user: str,
                             tag_hash: str,
                             table_name: str,
                             record_id: str,
                             result: dict):
        """ Create a (tag_hash, table_name, record_id) tag reference if a unique triplet did not already exist

        Parameters
        ----------
        user: str
            user id
        tag_hash: str
            tag hash
        table_name: str
            table_name = asset_class/asset/asset_version
        record_id: str
            record id in its corresponding table of this reference
        result: dict
            a free form json object

        Return
        -------
        """
        record = cls.get_if_exists(TagQueries.tag_hash == tag_hash,
                                   TagQueries.table_name == table_name,
                                   TagQueries.record_id == record_id,
                                   include_deleted_records=True
                                   )
        if record:
            if record.is_deleted:
                # restore if soft deleted earlier
                record.restore()
        else:
            record = cls.create(user=user,
                                tag_hash=tag_hash,
                                table_name=table_name,
                                record_id=record_id,
                                result=result
                                )
        return record

    def to_dict(self, recurse=False, backrefs=False, fields=None, exclude=None):
        result = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields, exclude=None)
        return result

    @classmethod
    def compute_tag_hash(cls, tag_ids):
        """Compute tag hash given tag ids
        Note: why we did it based on id but not on values? Because the hash of ids are unique

        Parameters
        ----------
        tag_ids: list
            a list of tag ids of the tags in the tags table

        Return
        -------
        """
        tag_ids = list(map(lambda x: str(x), tag_ids))
        return FileUtils.string_md5(",".join(sorted(tag_ids)))

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()
