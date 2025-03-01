from __future__ import annotations
from .serializable import Serializable
from server_core.utils.logging import LoggingMixin
import os


class AssetVersion(LoggingMixin, Serializable):
    id: int = None
    number: str = None
    patch: dict = None
    parent: int = None
    commit_hash: str = None
    commit_message: str = None
    asset = None
    created_by: str = None  # time stamp
    created_at: str = None

    def __init__(self, asset=None):
        self.asset = asset

    @property
    def yaml_url(self):
        """returns remote url for the asset object"""
        if not self.asset.remote_url or not self.number:
            return None
        return os.path.join(self.asset.remote_url, f"version_{self.number}.yaml")

    def de_serialize(self, asset, data: dict) -> AssetVersion:
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
        return [
            "id",
            "number",
            "patch",
            "parent",
            "commit_hash",
            "commit_message",
            "created_by",
            "created_at"
        ]






