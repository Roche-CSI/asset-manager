import json
from uuid import UUID


def to_json(data):
    return json.dumps(data, indent=4, sort_keys=True, default=str, cls=UUIDEncoder)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
