import abc
from server_core.utils.logging import LoggingMixin
from collections import OrderedDict
from .objects import ObjectSet
from .contents.content_set import ContentSet
from .serializable import Serializable
from .asset_class import AssetClass
from .asset_version import AssetVersion

SERIALIZED_KEYS = OrderedDict(**{
    "id": str,
    "asset_class": dict,
    "seq_id": int,
    "owner": str,
    "version": str,
    "refs": list,
    "top_hash": str,
    "alias": str,
    "frozen": bool,
    # "root": str,
    # "parent": str,  # parent asset
    "objects": list,
    # "patch": dict,  # objects = prev_ver.objects + self.patch
    # "commit_hash": str,
    "created_by": str,  # can be different than owner if employee leaves
    "created_at": str,
    "modified_by": str,
    "modified_at": str,
})


class BaseAsset(LoggingMixin, Serializable):
    """this is the counterpart of Asset record in DB"""
    id: str = None
    asset_class: AssetClass = None
    seq_id: int = None
    owner: str = None  # user_id who creates the asset
    version: AssetVersion = None
    refs: list = []
    # patch: str = None
    # commit_hash: str = None
    top_hash: str = None
    # root: str = None  # root asset
    # parent: str = None  # parent asset
    alias = None
    frozen = False
    created_by: str = None  # time stamp
    created_at: str = None
    modified_by: str = None
    modified_at: str = None
    objects: ObjectSet = None
    contents: ContentSet = None

    def __init__(self):
        self.objects = ObjectSet(asset=self)
        self.contents = ContentSet(asset=self)
        self.asset_class = AssetClass(asset=self)
        self.version = AssetVersion(asset=self)

    @abc.abstractmethod
    def de_serialize(self, data):
        raise NotImplementedError

    def serialize(self) -> dict:
        data = {key: getattr(self, key) for key in self.__class__.serialize_fields()}
        data["objects"] = self.objects.serialize()
        data["asset_class"] = self.asset_class.serialize()
        data["version"] = self.version.serialize()
        return data

    @classmethod
    def serialize_fields(cls):
        return SERIALIZED_KEYS

    def default(self):
        """json.dumps() calls this"""
        return self.serialize()

