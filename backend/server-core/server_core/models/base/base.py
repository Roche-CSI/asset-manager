from __future__ import annotations
import warnings
import peewee
from peewee import *
from playhouse.postgres_ext import JSONField
import pytz
from datetime import datetime
import uuid
# import logging
from server_core.utils.logging import LoggingMixin
from playhouse.shortcuts import model_to_dict
from server_core.utils import convert_to_pst
from server_core.configs import Configs
from server_core.models import utils
from .status_enums import StatusEnums

#: placeholder so that we can change database config in runtime
db_proxy = DatabaseProxy()
# added '/' to CREATE_KEY, its disallowed as column name
# this avoids name collision with user defined attributes
KREATE_KEY = "__/called_from_create"
PUBLICK_KEY = "__/called_from_public"
USER_NOT_SET = "USER_NOT_SET"


STATUS_CHOICES = (
    (StatusEnums.PUBLIC, 'Public'),
    (StatusEnums.PRIVATE, 'Private'),
    (StatusEnums.DELETED, 'Deleted'),
    (StatusEnums.DEPRECATED, 'Deprecated'),
    (StatusEnums.OBSOLETE, 'Obsolete'),
    (StatusEnums.ARCHIVE_FLAGGED, 'Archive-Flagged'),
    (StatusEnums.ARCHIVED, 'Archived'),
)


class BaseModel(LoggingMixin, Model):
    statuses = StatusEnums
    """Base Models, all models inherit from this"""
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    created_at = DateTimeField(null=False, default=lambda: datetime.now(pytz.utc))
    created_by = CharField(null=False)  # user_id
    # do soft delete only otherwise, versioning will get corrupted
    status = IntegerField(choices=STATUS_CHOICES, default=1)
    soft_delete_at = DateTimeField(null=True, default=None)
    soft_delete_by = CharField(null=True, default=None)
    tags = JSONField(default=list)

    class Meta:
        database = db_proxy

    def to_dict(self, recurse=False, backrefs=False, fields=None, exclude=None):
        """converts model to dict
        fields: list of field names
        """
        # fields = self._meta.manytomany.items()
        result = utils.model_to_dict(self,
                                     recurse=recurse,
                                     backrefs=backrefs,
                                     exclude=exclude)
        # remove private fields from dict
        for key in result:
            val = result.get(key)
            if type(val) == datetime:
                result[key] = convert_to_pst(val)
            if type(val) == uuid.UUID:
                result[key] = str(val)

        if not fields:
            return result

        # pop any extra keys
        return {field: result.get(field) for field in fields if field in result}

    def private_fields(self) -> set:
        return {
            # self.__class__.status,
            self.__class__.soft_delete_at,
            self.__class__.soft_delete_by,
            # self.__class__.tags
        }

    @classmethod
    def private_field_names(cls) -> set:
        return {"status", "soft_delete_at", "soft_delete_by", "tags"}

    @classmethod
    def time_now(cls):
        return datetime.now(pytz.utc)

    @property
    def id_string(self):
        return str(self.id)

    @property
    def is_create(self):
        return getattr(self, KREATE_KEY) if hasattr(self, KREATE_KEY) else False

    @is_create.setter
    def is_create(self, x):
        setattr(self, KREATE_KEY, x)

    @property
    def is_deleted(self):
        return self.status == self.statuses.DELETED

    @classmethod
    def set_is_called_from_public(cls, x):
        setattr(cls, PUBLICK_KEY, x)

    @classmethod
    def get_is_called_from_public(cls):
        return getattr(cls, PUBLICK_KEY) if hasattr(cls, PUBLICK_KEY) else False

    @classmethod
    def create(cls, user=None, **query):
        if "created_at" in query:
            # this is auto assigned so we ignore any user passed in values
            _ = query.pop("created_at")
        if "id" in query:
            query["id"] = cls.validate_id(id=query.get("id"))

        query["created_by"] = query.get("created_by") or user
        inst = cls(**query)
        inst.is_create = True
        inst.save(user, force_insert=True)
        inst.is_create = False
        return inst

    @classmethod
    def validate_id(cls, id):
        # raise Exception for id, if user passed None by mistake
        if not id:
            raise Exception("id can not be null")
        if type(cls.id) is peewee.UUIDField:
            if type(id) is not peewee.UUIDField:
                id = uuid.UUID(id)
        return id

    def save(self, user=USER_NOT_SET, force_insert=False, only=None):
        """make user explicit, should throw error"""
        if not user or user == USER_NOT_SET:
            raise ValueError("missing required parameter: user")
        if isinstance(self.status, str):
            # try to cast it to the correct status
            self.status = StatusEnums.from_string(self.status)
        return super().save(force_insert=force_insert, only=only)

    def restore(self):
        """ Restores an object. Un-flags permanent deletion
        This is implemented using model.update instead of model.save.
        model.save enforces readonly controls and doesn't allow readonly instances to be modified
        but a readonly instance can be flagged for deletion and restored
        """
        super(BaseModel, self.__class__).update(status=self.statuses.PUBLIC,
                                                soft_delete_by=None,
                                                soft_delete_at=None).where(self._pk_expr()).execute()

    @classmethod
    def soft_delete(cls, user):
        return super(BaseModel, cls).update(status=cls.statuses.DELETED,
                                            soft_delete_by=user,
                                            soft_delete_at=datetime.now()
                                            )

    # @classmethod
    # def logger(cls) -> logging.Logger:
    #     return logging.getLogger(cls.__name__)

    @classmethod
    def delete(cls, user, permanently=False):
        """override - ALLOW only soft delete"""
        if permanently:
            return super(BaseModel, cls).delete()
        else:
            return cls.soft_delete(user=user)

    def delete_instance(self, user, permanently=False, recursive=False, delete_nullable=False):
        """override - allow only soft delete"""
        if recursive:
            dependencies = self.dependencies(delete_nullable)
            for query, fk in reversed(list(dependencies)):
                model = fk.model
                if fk.null and not delete_nullable:
                    model.update(**{fk.name: None}).where(query).execute()
                else:
                    model.delete(user, permanently).where(query).execute()
        return type(self).delete(user, permanently).where(self._pk_expr()).execute()

    @property
    def status_label(self):
        return dict(STATUS_CHOICES)[self.status]

    @classmethod
    def public(cls):
        cls.set_is_called_from_public(True)
        result = cls.select().where(cls.status == 1)  # cls.statuses.PUBLIC is throwing error
        cls.set_is_called_from_public(False)
        return result

    # @classmethod
    # def list(cls, *fields, include_deleted_records=False):
    #     if include_deleted_records:
    #         sql = cls.select(*fields)
    #     else:
    #         cls.set_is_called_from_public(True)
    #         sql = cls.select(*fields).where(cls.status == cls.statuses.PUBLIC)
    #         cls.set_is_called_from_public(False)
    #     return sql

    # @classmethod
    # def select(cls, *fields):
    #     if not cls.get_is_called_from_public():
    #         # inform user to use Public instead
    #         warnings.warn("Please use public() instead of select()")
    #     cls.set_is_called_from_public(False)
    #     return super(BaseModel, cls).select(*fields)

    @classmethod
    def get(cls, *query, **filters):
        """override get to return only public objects"""
        sq = cls.select()
        if query:
            # Handle simple lookup using just the primary key.
            if len(query) == 1 and isinstance(query[0], int):
                sq = sq.where(cls._meta.primary_key == query[0])
            else:
                sq = sq.where(*query)
        if filters:
            sq = sq.filter(**filters)
        return sq.get()

    @classmethod
    def get_or_create(cls, user=None, **kwargs):
        defaults = kwargs.pop('defaults', {})
        query = cls.select()
        for field, value in kwargs.items():
            query = query.where(getattr(cls, field) == value)

        try:
            return query.get(), False
        except cls.DoesNotExist:
            try:
                if defaults:
                    kwargs.update(defaults)
                with cls._meta.database.atomic():
                    return cls.create(user=user, **kwargs), True
            except IntegrityError as exc:
                try:
                    return query.get(), False
                except cls.DoesNotExist:
                    raise exc

    @classmethod
    def get_if_exists(cls, *query, include_deleted_records=False, **filters) -> BaseModel:
        try:
            if not include_deleted_records:
                return cls.get(*query, **filters)
            else:
                return cls._get_including_deleted_records(*query, **filters)
        except DoesNotExist as e:
            cls.logger().info(e)
            return None

    @classmethod
    def _get_including_deleted_records(cls, *query, **filters):
        """override get to return only public objects"""
        sq = cls.select()
        if query:
            # Handle simple lookup using just the primary key.
            if len(query) == 1 and isinstance(query[0], int):
                sq = sq.where(cls._meta.primary_key == query[0])
            else:
                sq = sq.where(*query)
        if filters:
            sq = sq.filter(**filters)
        return sq.get()

    def yaml_data(self):
        return {
            "data": self.to_dict(fields=self.__class__.yaml_fields()),
            "url": self.yaml_url
        }

    @property
    def yaml_url(self):
        raise NotImplementedError

    @classmethod
    def yaml_fields(cls):
        """Subclass must implement"""
        raise NotImplementedError

    @property
    def configs(self):
        return Configs.shared()

    @classmethod
    def batch_insert(cls, user: str, data: list) -> list:
        """bulk update in batches"""
        time_now = cls.time_now()
        for item in data:
            item["created_by"] = item.get("created_by") or user
            item["created_at"] = time_now

        created = []
        # do 1000 at a time
        # note: profiled on 77,000 rows in ContentsModel, there is not much performance gain after 1000
        # creating 1 at a time i.e. cls.create -> 147.32 sec
        # batch_size: 1000 -> 12.67 seconds
        # batch_size: 20000 -> 12.65 seconds
        for chunk in chunked(data, 1000):
            inserted = cls.insert_many(chunk).on_conflict_ignore().execute()
            ids = list(map(lambda x: x[0], inserted))
            created += ids
        return created

    @classmethod
    def batch_read(cls, ids: list):
        """efficient querying of large number of rows.
        - this is much faster than doing select().join().execute(), which returns an iterator
        - note: this is not recursive, so for foreign-key relations we need to fetch manually
        https://github.com/coleifer/peewee/issues/1177
        """
        if not ids:
            return []
        query = cls.batch_read_query(ids=ids)
        result = list(map(lambda x: x, query.dicts()))
        for obj in result:
            for key in cls.private_field_names():
                del obj[key]
        return result

    @classmethod
    def batch_read_query(cls, ids: list) -> peewee.ModelSelect:
        """subclass can override"""
        # https://peewee.readthedocs.io/en/latest/peewee/query_operators.html
        return cls.select().where(cls.id << ids)
