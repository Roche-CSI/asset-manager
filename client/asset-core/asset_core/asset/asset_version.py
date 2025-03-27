from __future__ import annotations

import os.path
from datetime import datetime

from packaging import version

from asset_core.plugins import utils, exceptions, LoggingMixin
from .serializable import Serializable

ROOT_VERSION_NUMBER = "0.0.0"


class AssetVersion(LoggingMixin, Serializable):
    """Represents a version of an asset, including metadata and patch information."""

    id: int = None
    number: str = None
    patch: dict = None
    parent: AssetVersion = None
    commit_hash: str = None
    commit_message: str = None
    asset = None
    created_by: str = None  # time stamp
    created_at: str = None
    size: int = None

    def __init__(self, asset=None, **kwargs):
        """Initializes the AssetVersion object with optional asset and other attributes.

        Parameters
        ----------
        asset
            The asset associated with this version.
        **kwargs
            Additional keyword arguments for version attributes.
        """
        self.asset = asset
        for key in kwargs:
            setattr(self, key, kwargs.get(key))

    def de_serialize(self, asset, data: dict, fields=None) -> AssetVersion:
        """Deserializes version data into an AssetVersion object.

        Parameters
        ----------
        asset
            The asset associated with this version.
        data : dict
            The data to deserialize.
        fields : list, optional
            The fields to include in the deserialization.

        Returns
        -------
        AssetVersion
            The deserialized AssetVersion object.
        """
        if not data:
            return None
        self.asset = asset
        self.auto_save = False
        fields = fields or self.__class__.serialize_fields()
        for key in fields:
            val = data.get(key)
            if type(val) is datetime:
                val = utils.convert_to_pst(val)
            setattr(self, key, val)

        if self.parent and type(self.parent) is dict:
            parent = AssetVersion()
            parent.de_serialize(asset=None, data=self.parent)
            self.parent = parent

        self.auto_save = True

    def serialize(self, fields=None) -> dict:
        """Serializes the AssetVersion object into a dictionary.

        Parameters
        ----------
        fields : list, optional
            The fields to include in the serialization.

        Returns
        -------
        dict
            The serialized version data.
        """
        fields = fields or self.__class__.serialize_fields()
        result = {key: getattr(self, key) for key in fields}
        if "parent" in fields and type(result.get("parent")) is AssetVersion:
            result["parent"] = self.parent.serialize()
        return result

    def default_value(self) -> dict:
        """Returns a dictionary with default values for the serialized fields.

        Returns
        -------
        dict
            The dictionary with default values.
        """
        return {key: self._default_for_key(key) for key in self.__class__.serialize_fields()}

    def _default_for_key(self, key):
        """Returns the default value for a given key.

        Parameters
        ----------
        key : str
            The key for which to get the default value.

        Returns
        -------
        Any
            The default value for the key.
        """
        if type(getattr(self, key)) is dict:
            return {}
        elif type(getattr(self, key)) is list:
            return []
        else:
            return None

    def is_empty(self) -> bool:
        """Checks if the version is empty (no fields have values).

        Returns
        -------
        bool
            True if the version is empty, False otherwise.
        """
        for key in self.__class__.serialize_fields():
            if getattr(self, key):
                return False
        return True

    @classmethod
    def serialize_fields(cls) -> list:
        """Returns a list of fields that should be serialized.

        Returns
        -------
        list
            The list of serializable fields.
        """
        return [
            "id",
            "number",
            "patch",
            "parent",
            "commit_hash",
            "commit_message",
            "created_by",
            "created_at",
            "size"
        ]

    @property
    def is_temp(self) -> bool:
        """Checks if the version is a temporary version.

        Returns
        -------
        bool
            True if the version is temporary, False otherwise.
        """
        return self.__class__.is_temp_version(number=self.number)

    @classmethod
    def is_temp_version(cls, number=None, name=None) -> bool:
        """Checks if the given version number or name represents a temporary version.

        Parameters
        ----------
        number : str, optional
            The version number to check.
        name : str, optional
            The name to check.

        Returns
        -------
        bool
            True if the version is temporary, False otherwise.
        """
        number = number or cls.parse_name(name=name).get("version")
        if type(number) is str and number.startswith("temp_"):
            return True
        return False

    @property
    def name(self) -> str:
        """Returns the name of the asset version.

        Returns
        -------
        str
            The name of the asset version.
        """
        return f"{self.asset.name}/{self.number}"

    @classmethod
    def parse_name(cls, name, default_to_root=True) -> dict:
        """Parses the asset name into components.

        Parameters
        ----------
        name : str
            The asset name to parse.
        default_to_root : bool, optional
            Whether to default to the root version number if not specified.

        Returns
        -------
        dict
            The parsed components of the asset name. class_name, seq_id, version, alias, extras.

        Raises
        ------
        InvalidAssetNameError
            If the asset name is invalid.
        InvalidVersionError
            If the version is invalid.
        """
        if not name:
            raise exceptions.InvalidAssetNameError("asset name can not be null")

        parts: list = name.split("/")
        if len(parts) < 2:
            raise exceptions.InvalidAssetNameError(f"invalid asset name: {name}")

        # user passed just class_name and seq_id, so we need to add version
        result = {"class_name": parts[0]}
        if utils.is_integer(parts[1]) or str(parts[1]).startswith("temp_"):
            result["seq_id"] = parts[1]
            result["alias"] = None
        else:
            result["alias"] = parts[1]
            result["seq_id"] = None

        if len(parts) == 2:
            # user passed just class_name and seq_id, so we need to add version
            result["version"] = ROOT_VERSION_NUMBER if default_to_root else None
        else:
            if cls.is_valid_format(ver_number=parts[2]):
                result["version"] = parts[2]
            else:
                message = f"invalid asset name:{name}\n"
                message += """asset name can be:
                 - <asset-class>/<sequence>/<version>
                 - <asset-class>/<alias>/<version>
                """
                raise exceptions.InvalidVersionError(msg=f"invalid version: {parts[2]}, {message}")

            result["extras"] = "/".join(parts[3:]) if len(parts) > 3 else None
        return result

    @classmethod
    def get_name(cls, *comps) -> str:
        """Constructs an asset name from components.

        Parameters
        ----------
        *comps
            The components of the asset name.

        Returns
        -------
        str
            The constructed asset name.

        Raises
        ------
        InvalidVersionError
            If the asset name is invalid.
        """
        if len(comps) != 3:
            raise exceptions.InvalidVersionError(msg="invalid asset name")
        return os.path.join(*comps)

    @classmethod
    def is_valid_format(cls, ver_number: str) -> bool:
        """Checks if the version number is in a valid format.

        Parameters
        ----------
        ver_number : str
            The version number to check.

        Returns
        -------
        bool
            True if the given version number adheres to major.minor.patch, False otherwise.
        """
        if not ver_number:
            return False
        if len(ver_number.split(".")) != 3:
            return False
        try:
            return bool(version.Version(ver_number))
        except version.InvalidVersion:
            return False
