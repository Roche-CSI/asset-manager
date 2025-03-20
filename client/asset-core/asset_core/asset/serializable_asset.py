from collections import OrderedDict

from asset_contents.content_set import ContentSet
from asset_core.objects import ObjectSet
from .asset_class import AssetClass
from .asset_version import AssetVersion
from .base_asset import BaseAsset
from .refs import AssetRefSet
from .serializable import Serializable
from .status_enums import StatusEnums

SERIALIZED_KEYS = OrderedDict(**{
    "id": str,
    "asset_class": dict,
    "seq_id": int,
    "owner": str,
    "version": dict,
    "refs": list,
    "top_hash": str,
    "alias": str,
    "title": str,
    "description": str,
    "objects": list,
    "created_by": str,  # can be different from owner if employee leaves
    "created_at": str,
    "modified_by": str,
    "modified_at": str,
    "tags": list,
    "status": int,
    "metadata": dict,
    "attributes": dict,
    "frozen": bool
})


class SerializableAsset(BaseAsset, Serializable):
    """this is the counterpart of BaseAsset record in DB"""
    id: str = None
    asset_class: AssetClass = None
    seq_id: int = None
    owner: str = None  # user_id who create the node
    version: AssetVersion = None
    top_hash: str = None
    alias: str = None
    title: str = None
    description: str = None
    tags: list = None
    frozen: bool = False
    created_by: str = None  # time stamp
    created_at: str = None
    modified_by: str = None
    modified_at: str = None
    status: int = None
    refs: AssetRefSet = None
    objects: ObjectSet = None
    contents: ContentSet = None
    metadata: dict = None
    attributes: dict = None

    def __init__(self, id=None):
        self.auto_save = False
        self.id = id
        self.asset_class = AssetClass()
        self.objects = ObjectSet(asset=self)
        self.contents = ContentSet(asset=self)
        self.version = AssetVersion(asset=self)
        self.refs = AssetRefSet(asset=self)
        self.status = StatusEnums.default()
        self.auto_save = True

    def serialize(self, fields=None) -> dict:
        fields = fields or self.__class__.serialize_fields().keys()
        data = {key: getattr(self, key) for key in fields}
        data["objects"] = self.objects.serialize()
        data["asset_class"] = self.asset_class.serialize()
        data["version"] = self.version.serialize()
        data["refs"] = self.refs.serialize()

        for key in data:
            if not data.get(key):
                data[key] = self.default_value(key)

        return data

    def de_serialize(self, data: dict = None):
        self.auto_save = False
        data = data or (self.db.data() if self.db else None)
        if data:
            for key in self.__class__.serialize_fields():
                if key in data:
                    if key == "objects":
                        self.objects.de_serialize(obj_data=data.get(key) or [])
                    elif key == "asset_class":
                        self.asset_class.de_serialize(asset=self, data=data.get(key))
                    elif key == "version":
                        self.version.de_serialize(asset=self, data=data.get(key))
                    elif key == "refs":
                        self.refs.de_serialize(data=data.get(key, []))
                    else:
                        setattr(self, key, data.get(key))
        self.top_hash = self.top_hash or self.asset_class.id
        self.auto_save = True

    @classmethod
    def serialize_fields(cls):
        return SERIALIZED_KEYS

    @classmethod
    def asset_table_fields(cls):
        """fields for only the asset table in db"""
        return [
            "id",
            "asset_class",
            "seq_id",
            "owner",
            "top_hash",
            "alias",
            "frozen",
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
        ]

    def save(self):
        """saves the attributes to yaml"""
        self.db.update(**self.serialize())

    def default(self):
        """json.dumps() calls this"""
        return self.serialize()

    @property
    def db(self):
        """subclass must override"""
        raise NotImplementedError

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if self.auto_save and self.db:
            if key in self.__class__.serialize_fields():
                if key == "objects":
                    # serialize and update
                    data = {key: [obj.serialize() for obj in self.objects]}
                    self.db.update(**data)
                elif key == "asset_class":
                    self.db.update(**{key: self.asset_class.serialize()})
                else:
                    self.db.update(**{key: value})

    def add_inputs(self, inputs: list):
        """adds a list of inputs to a node"""
        curr_inputs = self.inputs
        for i in inputs:
            if i in curr_inputs:
                raise ValueError(f"{i} already exists and can not be added")
            curr_inputs.append(i)
        self.inputs = curr_inputs

    def default_value(self, key):
        if key == "owner":
            return self.repo.store.user_id
        elif type(getattr(self, key)) is dict:
            return {}
        elif type(getattr(self, key)) is list:
            return []
        elif type(getattr(self, key)) is ObjectSet:
            return []
        elif type(getattr(self, key)) is bool:
            return False
        else:
            return None

    def update(self, saved):
        """Updates local yaml with data returned from server
        Parameters
        ----------
        saved: dict
            Response from Server

        Returns
        -------

        """
        # pop asset_class, we have all the details already
        _ = saved.pop("asset_class")
        self.db.update(**saved)
