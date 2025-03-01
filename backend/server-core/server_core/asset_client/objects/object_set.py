from server_core.asset_client.objects.object import Object
from collections.abc import Callable
from server_core.utils import string_to_timestamp
from server_core.utils.better_set import BetterSet
from server_core.utils.file_utils import FileUtils
import os


class ObjectSet(BetterSet):
    """Custom Set for Objects"""
    asset = None
    _edit_restricted = True

    def __init__(self, *args, asset=None):
        super().__init__(*args)
        self.asset = asset

    def __copy__(self):
        return ObjectSet(*self.items, asset=self.asset)

    @property
    def hash(self):
        object_ids = list(map(lambda x: x.id, self))
        return FileUtils.string_md5(",".join(sorted(object_ids)))  # sort it to ignore ordering

    def yaml_url(self, url_id):
        """returns remote url for the asset object"""
        if not self.asset.remote_url:
            return None
        return os.path.join(self.asset.remote_url, "objects", f"{url_id}.yaml")

    def de_serialize(self, obj_data: list):
        # sort by timestamp
        obj_data.sort(key=lambda x: string_to_timestamp(x["created_at"]))
        self.extend(list(map(lambda x: Object.de_serialize(asset=self.asset, data=x), obj_data)))

    def add_objects(self, objects):
        """adds an object, updates states and file_meta"""
        self.extend(objects)

    def remove_objects(self, objects: list):
        for obj in objects:
            self.discard(obj)

    def serialize(self) -> list:
        return [obj.serialize() for obj in self]

    def filter(self, predicate: Callable = None) -> [Object]:
        """returns a dict of assets stored in asset-manifest
        Parameters:
            predicate: lambda function
        """
        if not predicate:
            return list(self)
        return [obj for obj in self if predicate(obj)]
