from __future__ import annotations
import abc
from server_core.utils.logging import LoggingMixin
from server_core.asset_client.state import ContentState
from server_core.utils.file_utils import FileUtils
from server_core.configs import Configs
import os
from server_core.gcp import parse_gcp_url
import aiohttp
import backoff

HASH_SEP = "_"
ID_SEP = ":"


class StorageSystems:
    GCS = "gs"
    BIGQUERY = "bq"
    URL = "url"
    DATABASE = "db"
    GCR = "gcr"


class Content(LoggingMixin):
    states = ContentState
    id: str = None
    hash: str = None
    mime_type: str = None
    size: int = None
    created_by: str = None
    created_at: str = None
    meta: dict = None
    asset = None

    linked_objects: set = None

    def __init__(self,
                 id=None,
                 hash=None,
                 mime=None,
                 size=None,
                 meta=None,
                 created_by=None,
                 created_at=None,
                 asset=None,
                 **kwargs):
        self.id = id
        self.hash = hash
        self.mime_type = mime
        self.size = size
        self.created_by = created_by
        self.created_at = created_at
        self.asset = asset
        self.meta = meta or {}
        for key in kwargs:
            setattr(self, key, kwargs.get(key))
        self.linked_objects = set()
        if not self.id:
            raise ValueError("missing required parameter id")

    def validate_kwargs(self, kwargs) -> dict:
        if not kwargs.get("id") and (not kwargs.get("hash_type") or not kwargs.get("hash_value")):
            raise ValueError("hash_type and hash_value are missing")

        kwargs["id"] = kwargs.get("id") or self.__class__.compute_id(kwargs.pop("hash_type"), kwargs.pop("hash_value"))
        return kwargs

    def serialize(self) -> dict:
        """serializes for storing in yaml"""
        return {field: getattr(self, field) for field in self.__class__.serialize_fields() if hasattr(self, field)}

    @classmethod
    def serialize_fields(cls):
        return [
            "id",
            "mime_type",
            "hash",
            "size",
            "meta",
            "created_by",
            "created_at"
        ]

    @classmethod
    def de_serialize(cls, asset, data: dict) -> Content:
        kwargs = data.copy()
        kwargs["asset"] = asset
        return cls(**kwargs)

    @classmethod
    def compute_id(cls, hash_type, hash_value):
        return ID_SEP.join([cls.storage_system_id(), cls.serialize_hash(hash_type, hash_value)])

    @property
    def storage_id(self) -> str:
        return self.__class__.parse_id(self.id)[0]

    # @property
    # def hash(self) -> str:
    #     return self.__class__.parse_id(self.id)[1]

    @property
    def hash_type(self):
        return self.__class__.parse_hash(self.hash)[0]

    @property
    def hash_value(self):
        return self.__class__.parse_hash(self.hash)[1]

    @classmethod
    def parse_id(cls, id: str) -> list:
        """returns a tuple of storage_id and hash"""
        return id.split(ID_SEP)

    @classmethod
    def parse_hash(cls, hash) -> list:
        """returns a tuple of hash_type and hash_value"""
        return hash.split(HASH_SEP)

    @property
    def file_id(self):
        """return urlsafe hash here"""
        return FileUtils.url_safe_md5(b64_md5=self.hash_value)

    @classmethod
    def get_file_id(cls, id: str):
        storage_id, hash = cls.parse_id(id)
        hash_type, hash_value = cls.parse_hash(hash=hash)
        return FileUtils.url_safe_md5(b64_md5=hash_value)

    @classmethod
    def serialize_hash(cls, hash_type, hash_value):
        if not hash_type or not hash_value:
            return None
        return HASH_SEP.join([hash_type, hash_value])

    @classmethod
    def deserialize_hash(cls, hash) -> tuple:
        """Deserializes hash
        Parameters
        ----------
        hash

        Returns
        -------
        tuple:
            Tuple of hash_type and hash_value
        """
        return hash.split(HASH_SEP)

    def __eq__(self, other):
        # required to make hashable
        if isinstance(other, Content):
            return self.__hash__() == other.__hash__()
        return False

    def __ne__(self, other):
        # required to make hashable
        return not self.__eq__(other)

    def __hash__(self):
        # required to make hashable
        return hash(self.id)

    @property
    def state(self):
        try:
            return self._state
        except AttributeError:
            # staged when they come to server
            self._state = self.states.STAGED
            return self._state

    @state.setter
    def state(self, x):
        self._state = x

    @property
    def is_proxy(self) -> bool:
        """proxy contents are not stored by asset manager"""
        return self.__class__.is_proxy_content(self.meta)

    @classmethod
    def is_proxy_content(cls, meta):
        return bool(meta and meta.get("proxy"))

    def can_download(self):
        """Indicates if a content data can be downloaded.
        Subclass can override for custom behaviour
        """
        return not self.is_proxy

    @property
    def can_stage(self):
        if self.is_proxy:
            return False
        return True

    @property
    def can_commit(self) -> bool:
        if not self.can_stage:
            # if it can't be staged - it can't be transferred to commmit
            return False
        return self.state in [self.states.STAGED, self.states.COMMITTING]

    @classmethod
    @abc.abstractmethod
    def storage_system_id(cls):
        raise NotImplementedError

    @property
    def remote_url(self):
        """returns remote url for the asset object"""
        if self.is_proxy:
            return self.meta["src"]
        else:
            return os.path.join(self.asset.contents.remote_url, self.file_id)

    @property
    def staging_url(self):
        """returns the staging url for the asset"""
        return os.path.join(self.asset.contents.staging_url, self.file_id)

    def read_url(self, class_id: str):
        """read url for content"""
        if self.is_proxy:
            return self.meta["src"]
        return os.path.join(Configs.shared().contents_url(staging=False), class_id, self.file_id)

    # @abc.abstractmethod
    # async def transfer_to_remote(self, **kwargs):
    #     raise NotImplementedError

    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
    async def transfer_to_remote(self, aio_client, callback=None):
        stg_bucket, stg_prefix = parse_gcp_url(url=self.staging_url)
        repo_bucket, repo_prefix = parse_gcp_url(url=self.remote_url)
        # 1. copy from src bucket to dest bucket
        copy_res: dict = await aio_client.copy(bucket=stg_bucket,
                                               object_name=stg_prefix,
                                               destination_bucket=repo_bucket,
                                               new_name=repo_prefix,
                                               timeout=60)

        if self.hash_value == copy_res.get("resource").get("md5Hash"):
            self.log.info("finished copying:{}".format(copy_res))
            self.state = self.states.COMMITTED
        else:
            self.log.error("error in copying file".format(copy_res))
            return

        # 2 delete
        delete_res = await aio_client.delete(bucket=stg_bucket,
                                             object_name=stg_prefix,
                                             timeout=60)
        self.log.info("deleted from staging:{}".format(delete_res))
        if callback:
            callback(copy_res)

    def default(self):
        """json.dumps() calls this"""
        return self.serialize()
