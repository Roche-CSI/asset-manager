import os.path
from collections.abc import Callable
from typing import Iterable

from asset_core.objects.asset_object import AssetObject
from asset_core.objects.object_factory import ObjectFactory
from asset_utils.common import BetterSet, exceptions
from asset_utils.utils import update_dict
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin


class ObjectSet(BetterSet, LoggingMixin):
    """Custom Set for Objects"""
    asset = None
    _edit_restricted = True

    def __init__(self, *args, asset=None):
        super().__init__(*args)
        self.asset = asset

    def __copy__(self):
        return ObjectSet(*self.items, asset=self.asset)

    def de_serialize(self, obj_data: list):
        self._edit_restricted = False
        for data in obj_data:
            _ = ObjectFactory().de_serialize(asset=self.asset, data=data)

        for obj in self:
            obj.set_state(self.get_states().get(obj.unique_repr))
            obj.content = self.asset.contents.add_content(obj.content)

        self._edit_restricted = True

    def add_objects(self, objects: [AssetObject], callback: Callable = None, save: bool = False):
        """add new objects an object, updates states and file_meta"""
        self._edit_restricted = False
        new_objects, updates, existing, tobe_replaced = self._find_delta(objects=objects)

        # make sure replaced objects are allowed to be updated
        # for example, group member objects or group objects can not be updated
        for obj in self:
            if not obj.can_update:
                raise exceptions.AssetException(f"asset contains a read only object {obj}, asset can not be updated")

        ignored = set()
        selected = new_objects.union(updates)
        idx = 1
        for object in objects:
            if object in selected:
                object.add_to_asset(asset=self.asset)
                object.link_to_store()
            else:
                ignored.add(self.get(object))
            if callback:
                callback(object)
                # print(idx)
                idx += 1

        # update states
        self.update_states(objects=selected)
        self.update_file_stats(objects=selected)
        self._edit_restricted = True
        if save:
            self.asset.contents.save()
            self.save()

        return new_objects, updates, ignored

    def _find_delta(self, objects: [AssetObject]):
        existing, updates, new_objects, tobe_replaced = set(), set(), set(), set()
        for obj in objects:
            if obj in self:
                # find by path
                found = self.get(obj)
                # compare id
                if found.id == obj.id:
                    # already exists
                    existing.add(obj)
                else:
                    updates.add(obj)
                    tobe_replaced.add(found)
            else:
                new_objects.add(obj)

        return new_objects, updates, existing, tobe_replaced

    def remove_objects(self, objects: list, save=False):
        self._edit_restricted = False
        states = self.get_states()
        for obj in objects:
            self.discard(obj)
            states.pop(obj.unique_repr, None)

        self._edit_restricted = True
        self.set_states(states)
        if save:
            self.save()

    def clear(self):
        self.remove_objects(self.items, save=True)

    def link(self,
             selected: [AssetObject] = None,
             linking_type: str = "copy",
             callback=None):
        status = {}
        for object in selected or self:
            try:
                status[object] = object.link_from_store(linking_type=linking_type, callback=callback)
            except exceptions.ContentNotAvailableError:
                status[object] = False

        self.update_file_stats(objects=self)
        self.asset.object_stats_db.update(**{"stats": self.get_file_stats()})
        return status

    def unlink(self, delete=True, callback=None):
        for object in self:
            object.unlink(delete=delete, callback=callback)

    def linked(self):
        for object in self:
            if not object.linked():
                return False
        return True

    def remove(self, item):
        if self._edit_restricted:
            raise Exception("remove is restricted please call remove_objects instead")
        super(ObjectSet, self).remove(item)

    def add(self, item: AssetObject):
        if self._edit_restricted:
            raise Exception("add is restricted please call add_objects instead")
        super(ObjectSet, self).add(item)

    def serialize(self) -> list:
        return [obj.serialize() for obj in self]

    @property
    def hash(self):
        object_ids = list(map(lambda x: x.id, self))
        return FileUtils.string_md5(",".join(sorted(object_ids)))  # sort it to ignore ordering

    def get_with_path(self, path):
        filtered = self.filter(lambda x: x.path == path)
        if len(filtered) > 0:
            return filtered[0]
        else:
            return None

    def filter(self, predicate: Callable = None) -> [AssetObject]:
        """returns a dict of assets stored in asset-manifest
        Parameters:
            predicate: lambda function
        """
        if not predicate:
            return list(self)
        return [obj for obj in self if predicate(obj)]

    def unlinked(self):
        return [obj for obj in self if not os.path.exists(obj.linked_path)]

    def get_states(self):
        try:
            return self._states
        except AttributeError:
            self._states = self.asset.states_db.get_object_states()
            return self._states

    def set_states(self, x: dict, save=False):
        self._states = x
        if save:
            self.asset.states_db.update(**{"object_states": self._states})

    def update_states(self, objects: [AssetObject], save=False):
        updates = {obj.unique_repr: obj.get_state() for obj in objects}
        self.set_states(update_dict(self.get_states(), updates), save)

    def get_file_stats(self):
        try:
            return self._file_stats
        except AttributeError:
            self._file_stats = self.asset.object_stats_db.get_stats()
            return self._file_stats

    def set_file_stats(self, x: dict, save=False):
        self._file_stats = x
        if save:
            self.asset.object_stats_db.update(**{"stats": self._file_stats})

    def update_file_stats(self, objects: Iterable[AssetObject], save=False):

        updates = {obj.unique_repr: obj.get_object_stat() for obj in objects}
        for key, val in updates.items():
            if val:
                updates[key] = val.serialize()

        file_stats = {
            **self.get_file_stats(),
            **updates
        }
        self.set_file_stats(file_stats, save=save)

    def get_object_by_id(self, id: str):
        for obj in self:
            if obj.id == id:
                return obj
        return None

    def find(self, source_paths: list):
        """Finds assets corresponding to the files
        Parameters:
            source_paths list of file paths
        """
        rel_paths = [os.path.relpath(path=os.path.abspath(src), start=self.asset.repo.fs_path)
                     for src in source_paths]
        result = self.filter(predicate=lambda x: x.path in rel_paths)
        self.log.info("results:{}".format(result))
        return result

    def save(self):
        self.asset.db.update(**{"objects": [obj.serialize() for obj in self]})
        self.asset.states_db.update(**{"object_states": self.get_states()})
        self.asset.object_stats_db.update(**{"stats": self.get_file_stats()})

    @property
    def size(self):
        if not hasattr(self, "_size"):
            self._size = sum([obj.content.size for obj in self.items])
        return self._size
