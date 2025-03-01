from .base import BaseModel
from peewee import DateTimeField, CharField
from datetime import datetime


class ReadWriteModel(BaseModel):
    modified_at = DateTimeField(null=True)  # null true when created first time
    modified_by = CharField(null=True)

    def save(self, user=None, force_insert=False, only=None):
        # if not its coming from create flow, then update modified_at and modified_by
        if not self.is_create:
            self.modified_at = datetime.now()
            self.modified_by = user
        if only:
            only += [self.__class__.modified_at, self.__class__.modified_by]
        return super().save(user, force_insert, only)