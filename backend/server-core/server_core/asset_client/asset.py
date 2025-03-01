from server_core.utils.file_utils import FileUtils
import os
from .base_asset import BaseAsset
from server_core.configs import Configs
from .contents import ContentUploader


class Asset(BaseAsset):
    configs = None
    user: str = None

    def __init__(self, user, data):
        super(Asset, self).__init__()
        self.de_serialize(data)
        self.configs = Configs.shared()
        self.user = user

    def __str__(self):
        return os.path.join(self.asset_class.name, self.seq_id or "pending", self.version or "pending")

    def de_serialize(self, data):
        for key in self.__class__.serialize_fields():
            if key in data:
                if key == "objects":
                    self.objects.de_serialize(obj_data=data.get(key) or [])
                elif key == "asset_class":
                    self.asset_class.de_serialize(asset=self, data=data.get(key))
                elif key == "version":
                    self.version.de_serialize(asset=self, data=data.get(key))
                else:
                    setattr(self, f"{key}", data.get(key))

    @property
    def remote_url(self):
        if not self.id:
            return None
        return os.path.join(self.configs.assets_url, self.asset_class.id, str(self.seq_id))

    @property
    def yaml_url(self):
        if not self.id:
            return None
        return os.path.join(self.remote_url, "asset.yaml")

    @property
    def hash(self):
        object_ids = list(map(lambda x: x.id, self.objects))
        return FileUtils.string_md5(",".join(sorted(object_ids)))

    def commit_contents(self):
        """commit contents to bucket or their respective storage"""
        content_uploader = ContentUploader(self.contents)
        content_uploader.commit_contents()

