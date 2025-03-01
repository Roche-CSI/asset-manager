from __future__ import annotations
from .serializable import Serializable
from server_core.utils.logging import LoggingMixin


class AssetClass(LoggingMixin, Serializable):
    id: str = None
    name: str = None
    project: str = None
    asset = None

    def __init__(self, id=None, name=None, asset=None, project=None):
        self.id = id
        self.name = name
        self.project = project
        self.asset = asset

    def de_serialize(self, asset, data: dict) -> AssetClass:
        if not data:
            return None
        self.auto_save = False
        for key in self.__class__.serialize_fields():
            setattr(self, key, data.get(key))
        self.auto_save = True

    def serialize(self) -> dict:
        return {key: getattr(self, key) for key in self.__class__.serialize_fields()}

    @classmethod
    def serialize_fields(cls):
        return ["id", "name", "project"]






