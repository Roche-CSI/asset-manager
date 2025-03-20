import json
from dataclasses import dataclass
from typing import Any, Type

from asset_utils.common import exceptions
from asset_utils.utils import is_integer


@dataclass
class SettingsProp:
    """Settings property class to hold the settings for the application"""

    value: Any = None  # bool | str | int | float
    data_type: Type = str  # default is string
    unit: str = None  # seconds, bool, bytes, etc
    name: str = None  # environment variable name
    help: str = None  # help message

    def description(self, is_default=None):
        return f"{self.value}: {self.unit} [{'factory' if is_default else 'user-defined'}] - {self.help}"

    def validate(self, value: Any, data_type: Type = None):
        """validate the value against the data type"""
        data_type = data_type or self.data_type
        if data_type is int:
            if not is_integer(value):
                raise exceptions.AssetException(f"Invalid integer value for {self.name}: {value}")
            return int(value)
        elif data_type is float:
            try:
                return float(value)
            except ValueError as e:
                raise exceptions.AssetException(f"Invalid float value for {self.name}: {value}") from e
        elif data_type is bool:
            # user only allowed true/false strings
            if value not in ["true", "false", True, False]:
                raise exceptions.AssetException(f"Invalid boolean value for {self.name}: {value}")
            return bool(value == "true" or value is True)
        elif data_type is str:
            # make sure the value is a string
            if isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
                raise exceptions.AssetException(f"Invalid string value for {self.name}: {value}")
            return value
        elif data_type is dict:
            # we add the pair to the existing dict
            if value and isinstance(value, str):
                # verify that the user passed the string in correct format i.e. ':' separated
                parts = value.split(":")
                # as the bucket url will have a ':' in it, we wll always have 3 parts
                if len(parts) != 3:
                    e = exceptions.AssetException(f"Invalid dict value for {self.name}: {value}")
                    e.logs.add("Use 'bucket_url:mount_path' to add a new mount path")
                    raise e
                bucket_url = f"{parts[0]}:{parts[1].strip()}"
                self.value[bucket_url] = parts[2].strip()
                return self.value

            if not isinstance(value, dict):
                raise exceptions.AssetException(f"Invalid dict value for {self.name}: {value}")
            return value

    @classmethod
    def to_string(cls, value):
        return json.dumps(value)

    @classmethod
    def from_string(cls, value):
        return json.loads(value)
