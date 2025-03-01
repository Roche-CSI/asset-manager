import os
import logging

logger = logging.getLogger(__file__)
HASH_SEP = "$"


class AssetObject:
    url_id: str
    path: str  # relative path inside assets repo root
    hv: str  # hash
    ht: str  # defaults is md5
    content_type: str
    asset = None

    def __init__(self, path, hv, ht, url_id, ct=None, asset=None):
        self.path = path
        self.hv = hv
        self.ht = ht
        self.url_id = url_id
        self.content_type = ct
        self.asset = asset

    def serialize(self) -> dict:
        """serializes for storing in yaml"""
        return {self.url_id: {'path': self.path,
                              "hash": f"{self.ht}{HASH_SEP}{self.hv}",
                              "ct": self.content_type}
                }

    @property
    def remote_url(self):
        """returns remote url for the asset object"""
        return os.path.join(self.asset.objects_url, self.id)

    @property
    def staging_url(self):
        """returns the staging url for the asset"""
        return os.path.join(self.asset.staging_url, self.id)