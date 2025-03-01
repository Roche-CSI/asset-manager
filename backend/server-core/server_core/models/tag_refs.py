from peewee import *
from .base.read_write import ReadWriteModel
from .tags import Tags


class TagRefs(ReadWriteModel):
    tag_id = ForeignKeyField(Tags, backref='tags', null=False, on_delete='CASCADE')
    table_name = CharField(null=False)
    record_id = CharField(null=False)
    is_primary = BooleanField(null=False)

    class Meta:
        indexes = (
            (('tag_id', 'table_name', 'record_id'), True),
            (('tag_id', 'table_name'), False),
            (('table_name', 'record_id'), False),
        )

    @classmethod
    def create_if_not_exists(cls,
                             user: str,
                             tag_id: str,
                             table_name: str,
                             record_id: str,
                             is_primary: bool = False):
        """ Create a (tag_id, table_name, record_id, is_primary) tag reference if a unique record did not already exist

        Parameters
        ----------
        user: str
            user id
        tag_id: str
            tag id
        table_name: str
            table_name = asset_class/asset/asset_version
        record_id: str
            record id in its corresponding table of this reference
        is_primary: bool
            True if the tag ref is a primary key

        Return
        -------
        """
        record = cls.get_if_exists(TagRefs.tag_id == tag_id,
                                   TagRefs.table_name == table_name,
                                   TagRefs.record_id == record_id,
                                   TagRefs.is_primary == is_primary,
                                   include_deleted_records=True
                                   )
        if record:
            if record.is_deleted:
                # restore if soft deleted earlier
                record.restore()
        else:
            record = cls.create(user=user,
                                tag_id=tag_id,
                                table_name=table_name,
                                record_id=record_id,
                                is_primary=is_primary
                                )
        return record

    def to_dict(self, recurse=False, backrefs=False, fields=None, exclude=None):
        result = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields, exclude=None)
        if recurse:  # add tag information
            result["tag_name"] = result["tag_id"]["tag_name"]
            result["tag_value"] = result["tag_id"]["tag_value"]
        return result

    @classmethod
    def list_tag_refs(cls, table_name: str, record_id: str, recurse: bool = False) -> []:
        """finds the TagRef records from the given table_name and record_id
        """
        query = TagRefs.select().where(
            (TagRefs.table_name == table_name) &
            (TagRefs.record_id == record_id)
        )
        return query.execute()

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()


# Add a partial index on table_name and record_id where is_primary is true
# Ref: https://docs.peewee-orm.com/en/latest/peewee/models.html?highlight=table%20generation#advanced-index-creation
TagRefs.add_index(TagRefs.table_name, TagRefs.record_id, where=(TagRefs.is_primary == 1))

