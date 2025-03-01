import json
from .object_set import ObjectSet


class ObjectsDiff:
    """class to manage differences between to object_sets"""
    added = []
    removed = []

    @classmethod
    def deserialize(cls, data: dict):
        """dict to ObjectsDiff"""
        diff = ObjectsDiff
        for field in cls.serialize_fields():
            setattr(diff, data.get(field))
        return diff

    def compute_diff(self, from_objects=None, to_objects=None):
        """For diff we only store pointers, this optimizes storage, downloads.
        The added advantage is that:
          - allows us the flexibility of schema modifications in future
          - implement the feature branching and merge should we decide to do so
        """

        from_objects = from_objects or ObjectSet()
        to_objects = to_objects or ObjectSet()

        # allow for lists also
        if type(from_objects) is list:
            from_objects = set(from_objects)

        if type(to_objects) is list:
            to_objects = set(to_objects)

        removed = []
        added = []
        for item in from_objects:
            if item not in to_objects:
                removed.append(item.id)

        for item in to_objects:
            if item not in from_objects:
                added.append(item.id)

        self.added = added
        self.removed = removed

    def serialize(self):
        """converts ObjectDiff to dict"""
        return {field: getattr(self, field) for field in self.__class__.serialize_fields()}

    @classmethod
    def serialize_fields(cls):
        return ["removed", "added"]


