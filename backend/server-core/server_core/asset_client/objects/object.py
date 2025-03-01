from __future__ import annotations
from server_core.asset_client.contents.content import Content
from server_core.utils.logging import LoggingMixin


class Object(LoggingMixin):
    HASH_SEP = "_"
    ID_SEP = "::"

    id: str
    url_id: int
    created_by: str
    created_at: str
    # path: str  # object description
    content: Content
    asset = None  # parent asset

    def __init__(self,
                 id,
                 url_id,
                 content=None,
                 created_by=None,
                 created_at=None,
                 asset=None):
        """
        Parameters
        ----------
        path: str
            object description, for file mime_type objects, this the path inside repo
        content: Content
            content of the Object
        created_by: str
            user id
        created_at: str
            timestamp
        asset: Asset
            reference to the Asset to which the object belongs
        """
        # self.path = path
        self.id = id
        self.url_id = url_id
        self.asset = asset
        self.created_by = created_by
        self.created_at = created_at
        self.content = content
        self.content.linked_objects.add(self)

    def __eq__(self, other):
        if isinstance(other, Object):
            return self.__hash__() == other.__hash__()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.unique_repr)

    @property
    def path(self):
        return self.__class__.parse_id(self.id)[1]
        # return self.id.split(self.__class__.ID_SEP)[1]

    @classmethod
    def parse_id(cls, id: str):
        return id.split(cls.ID_SEP)

    @classmethod
    def create_id(cls, content, path):
        if not path:
            raise Exception("required param path can not be null")
        if not content:
            raise Exception("required param content can not be null")
        content_id = content.id if isinstance(content, Content) else content
        return cls.ID_SEP.join([content_id, path])

    @property
    def unique_repr(self):
        """return a unique representation of the object
        we can't use md5 since user might add duplicate files
        so we use a combination of hash and path i.e. the object is same
        if both content and path are same
        """
        # return f"{self.path}:{self.hash}"
        return self.path

    @property
    def can_commit(self) -> bool:
        return self.content.state == Content.states.COMMITTED

    @classmethod
    def serialize_fields(cls):
        return [
            "id",
            "created_by",
            "created_at",
            "content"
        ]

    def serialize(self) -> dict:
        """serializes for storing in yaml"""
        fields = self.__class__.serialize_fields()
        data = {}
        for field in fields:
            val = getattr(self, field)
            data[field] = val if field != "content" else val.serialize()
        return data

    @classmethod
    def de_serialize(cls, asset, data: dict) -> Object:
        kwargs = data.copy()
        kwargs["asset"] = asset
        kwargs["content"] = asset.contents.de_serialize(asset=asset, data=data.get("content", {}))
        return cls(**kwargs)

    # @classmethod
    # def deserialize_hash(cls, hash) -> tuple:
    #     return hash.split(HASH_SEP)

