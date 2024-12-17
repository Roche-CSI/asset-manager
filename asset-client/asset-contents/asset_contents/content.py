from __future__ import annotations

import abc
import os

from asset_db import FileDB
from asset_pluggy.storage.blob import StorageData
from asset_utils.common import exceptions
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin
from .content_stat import ContentStat
from .content_state import ContentState

HASH_SEP = "_"
ID_SEP = ":"
PROXY_FLAG = "proxy_"
PROXY_SEP = ":"


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
    created_by: str = None
    created_at: str = None
    size: int = None
    meta: dict = None
    # non serialized fields
    linked_objects: set = None

    def __init__(self,
                 id=None,
                 mime=None,
                 size=None,
                 meta=None,
                 created_by=None,
                 created_at=None,
                 **kwargs):
        """
        Parameters
        ----------
        id: str
            id is hash_type$hash_value
        mime: str
             IANA mime_type of the file
        size: int
            content size in bytes
        meta: dict
            additional meta information about the content
        created_by: str
            username
        created_at: str
            time
        storage_name: str
        kwargs
        """
        self.id = id
        self.mime_type = mime
        self.size = size
        self.created_by = created_by
        self.created_at = created_at
        self.meta = meta or {}
        for key in kwargs:
            setattr(self, key, kwargs.get(key))
        self.linked_objects = set()
        if not self.id:
            raise ValueError("missing required parameter id")

    def validate_kwargs(self, kwargs) -> dict:
        if not kwargs.get("id") and (not kwargs.get("hash_type") or not kwargs.get("hash_value")):
            raise ValueError("hash_type and hash_value are missing")
        kwargs["hash"] = kwargs.get("hash") or self.__class__.serialize_hash(kwargs.pop("hash_type"),
                                                                             kwargs.pop("hash_value"))
        kwargs["id"] = kwargs.get("id") or self.__class__.compute_id(hash=kwargs["hash"],
                                                                     meta=kwargs["meta"],
                                                                     storage_name=kwargs.get("storage_name", None))
        return kwargs

    @property
    @abc.abstractmethod
    def can_download(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def can_upload(self):
        raise NotImplementedError

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, x):
        self._asset = x

    def add_to_asset(self, asset, object):
        self.asset = asset
        self.transfer_to_cache(src=object.linked_path)
        self.add_ref(object=object)
        self.add_to_store()
        self.set_state(self.__class__.states.PENDING)

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

    def prune(self):
        """prunes the content i.e. removes the file if there are no references"""
        file_stat = self.get_content_stat()
        if not file_stat.refs:
            self.clear_from_cache()

    @classmethod
    def compute_id(cls, hash: str, meta: dict = None, storage_name: str = None):
        if cls.is_proxy_content(meta=meta):
            if not meta.get("src"):
                raise exceptions.InvalidObjectSourceError()
            # the hash will always be md5 regardless of the content hash
            hash = f"{PROXY_FLAG}{cls.proxy_hash(src=meta.get('src'), content_hash=hash)}"
            # note: for proxy content we use the name of the storage
            storage_id = storage_name
        else:
            storage_id = cls.storage_system_id()

        if not storage_id:
            raise Exception("storage_id can not be null")
        return ID_SEP.join([storage_id, hash])

    @classmethod
    def proxy_hash(cls, src, content_hash):
        """The md5 hash used to compute the id for proxy content

        The content hash can be md5, sha1, etag etc.
        i.e. for s3, etag_"7b20247d9b4179ac46fdc4053e20db12"

        The proxy hash would be md5 of src and content_hash
        """
        return "md5_{}".format(FileUtils.string_md5(f"{src}{PROXY_SEP}{content_hash}", b64=True))

    @property
    def is_proxy(self) -> bool:
        """proxy contents are not stored by asset manager"""
        return self.__class__.is_proxy_content(self.meta)

    @classmethod
    def is_proxy_content(cls, meta):
        return bool(meta and meta.get("proxy"))

    @property
    def storage_id(self) -> str:
        return self.__class__.parse_id(self.id)[0]

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

    def exists(self, path=None) -> bool:
        """checks if the content exists locally

        Parameters
        ----------
        path: file path

        Returns
        -------

        """
        path = path or self.cache_path
        # verify file exists
        file_exists = os.path.exists(path) and os.path.isfile(path)
        # make sure the file size matches (we use this as a proxy instead of
        # computing the hash again, which is expensive)
        file_size = os.path.getsize(path) if file_exists else 0
        return file_exists and file_size == self.size

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

    def __repr__(self):
        return self.id

    @property
    def file_stats_db(self) -> FileDB:
        return self.asset.object_stats_db

    def transfer_to_cache(self, src):
        # copy-on-write copy of the file
        if not src or not os.path.exists(src):
            return  # applies to gcs, docker content etc
        if not self.exists():
            FileUtils.copy_file(src=src, dst=self.cache_path)

    def clear_from_cache(self, path=None):
        path = path or self.cache_path
        if os.path.exists(path):
            os.remove(path)

    def add_to_store(self, stat: ContentStat = None, save: bool = False):
        """adds the content to asset-store, it serves two primary objectives
        - content stat: to check if a content was modified after being added, user manually tampers data
        - ref counting: in asset-store prune we need to removed all unused content, so need to maintain a ref count
        Parameters
        ----------
        stat: ContentStat
        src: str
        save: bool

        Returns
        -------
        """
        # ref counting and edit history
        existing = self.get_content_stat()
        if not existing:
            if stat:
                # assign id to make sure its tagged correctly
                stat.id = self.file_id
            else:
                stat or self.compute_stat()
            self.set_content_stat(stat, save=save)

    def get_state(self):
        try:
            return self._state
        except AttributeError:
            self._state = self.asset.states_db.get_content_states().get(self.id)
            return self._state

    def set_state(self, x, save=False):
        self._state = x
        if save:
            self.asset.states_db.add_content_states(**{self.id: self._state})

    def get_content_stat(self) -> ContentStat:
        try:
            return self._content_stat
        except AttributeError:
            stored = self.asset.content_stats_db.get_stats().get(self.file_id) or {}
            self._content_stat = ContentStat.de_serialize(stored) if stored else None
            return self._content_stat

    def set_content_stat(self, x: ContentStat, save=False):
        self._content_stat = x
        if save:
            serialized = x.serialize() if x else None
            self.asset.content_stats_db.add_stats(**{self.file_id: serialized})

    @classmethod
    def storage_system_id(cls):
        if not os.getenv("ASSET_PROJECT_STORAGE_ID"):
            raise exceptions.InvalidStorageBackendError()
        return os.environ["ASSET_PROJECT_STORAGE_ID"]

    def compute_stat(self, path=None) -> ContentStat:
        """Calculates content stat like size etc.
        we need this for validating file integrity
        """
        path = path or self.cache_path
        if not self.exists(path):
            # user didn't download the asset but is modifying it, which is allowed
            return None
        stat = ContentStat(id=self.file_id, src=path)
        return stat

    def validate_checksum(self, content_path, callback=None):
        stats = self.compute_stat(content_path)
        if stats.size != self.size:
            self.log.error("error in downloading file")
            # delete the file
            self.clear_from_cache(content_path)
        else:
            # now compute hash and check
            hash_type, hash_val = self.__class__.compute_hash(content_path)
            if hash_type == self.hash_type and hash_val == self.hash_value:
                # valid download - update the content-stats in store
                self.add_to_store(stat=stats)
                if callback:
                    callback()
            else:
                self.log.error("error in downloading file")
                # delete the file
                self.clear_from_cache(content_path)

    @property
    def cache_path(self):
        """caching location of the object"""
        return os.path.join(self.asset.contents.cache_dir, self.file_id)

    @property
    def source_url(self):
        raise NotImplementedError

    def add_ref(self, object, save=False):
        self.linked_objects.add(object)
        # update file references
        stat = self.get_content_stat() or self.compute_stat(self.cache_path)
        if stat:
            stat.add_ref(os.path.join(self.asset.repo.id, object.path))
            self.set_content_stat(stat, save=save)

    def remove_ref(self, object, save=False):
        self.linked_objects.discard(object)
        # update file references
        stat = self.get_content_stat()
        if stat:
            stat.remove_ref(os.path.join(self.asset.repo.id, object.path))
            self.set_content_stat(stat, save=True)

    @property
    def can_stage(self) -> bool:
        # if proxy asset no need to upload
        # since we don't manage storage ourselves
        if self.is_proxy:
            return False
        return self.get_state() in [self.states.PENDING, self.states.STAGING]

    @classmethod
    @abc.abstractmethod
    def create(cls, storage_name: str, blob: StorageData, proxy: bool = False, **kwargs) -> Content:
        """creates and returns an asset object"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def compute_hash(cls, **kwargs):
        """Subclass must return hash of the underlying file"""
        raise NotImplementedError

    def default(self):
        """json.dumps() calls this"""
        return self.serialize()
