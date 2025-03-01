from peewee import *
from .base.read_only import ReadOnlyModel


class Tags(ReadOnlyModel):
    tag_name = CharField(null=False)
    tag_value = CharField(null=False)

    class Meta:
        indexes = ((('tag_name', 'tag_value'), True),)

    @classmethod
    def create_if_not_exists(cls,
                             user: str,
                             tag_name: str,
                             tag_value: str):
        """ Create a (tag_name, tag_value) tag if an unique pair did not already exist

        Parameters
        ----------
        user: user id
        tag_name: str
        tag_value: int
        TODO: add more fields: TBD

        Return
        -------
        """
        record = cls.get_if_exists(Tags.tag_name == tag_name,
                                   Tags.tag_value == tag_value,
                                   include_deleted_records=True
                                   )
        if record:
            if record.is_deleted:
                # restore if soft deleted earlier
                record.restore()
        else:
            record = cls.create(user=user,
                                tag_name=tag_name,
                                tag_value=tag_value,
                                )
        return record

    def to_dict(self, recurse=False, backrefs=False, fields=None, exclude=None):
        result = super().to_dict(recurse=recurse, backrefs=backrefs, fields=fields, exclude=None)
        return result

    @classmethod
    def validate_tags(cls, tags: list):
        """Validate a list of tags dict"""
        for tag in tags:
            tag_name = tag.get("tag_name")
            tag_value = tag.get("tag_value")
            if not tag_name or not tag_value:
                raise Exception(f'tag_name and tag_value cannot be empty: {tag_name, tag_value}')
            if ' ' in tag_name:
                raise Exception(f'tag_name cannot contain spaces: {tag_name}')
        return True

    @property
    def yaml_url(self):
        raise NotImplementedError()

    @classmethod
    def yaml_fields(cls):
        raise NotImplementedError()