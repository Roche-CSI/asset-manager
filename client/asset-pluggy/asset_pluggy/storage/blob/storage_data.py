from __future__ import annotations

import abc
import os
from typing import Any

from asset_pluggy.storage.urls import StorageURL
from asset_utils.common import exceptions
from asset_utils.utils.log_utils import LoggingMixin

PATH_SEPARATOR = "/"


class StorageData(LoggingMixin, metaclass=abc.ABCMeta):
    url: str
    host: str
    name: str
    size: int = None
    content_type: str = None
    hashes: dict = None
    path_in_asset: str = None  # relative path of the data with respect to the query url

    def __init__(self, data: Any, url_object: StorageURL):
        """Initializes a standardized blob objects from data.
        Each storage plugin must provide their own blob by extending this class

        Parameters
        ----------
        data: any
            gcs Blob in case GCS, in case of aws or other storage, it could be a dictionary
        """
        # sanitize by removing any slashes from front and end
        self.hashes = {}
        self.initialize(data=data, url_object=url_object)
        # calculate path_in_asset, we need this to check for overrides
        # for example, user might enter 2 different urls and the query results could be such that
        # the path_in_asset of two objects collide. In that case, we consider only the first blob
        self.path_in_asset = os.path.relpath(self.name, url_object.dir_name)
        self.validate()

    def __eq__(self, other: StorageData):
        return self.path_in_asset == other.path_in_asset

    def __hash__(self):
        return hash(self.path_in_asset)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.path_in_asset)

    def validation_attributes(self) -> list:
        # note: even though hash is required, we are deferring hash validation
        # to the time of usage instead of time of instantiation
        # refer: self.get_hash for more details
        return ["name", "url", "host"]

    def validate(self):
        """subclass can override"""
        required_attrs = self.validation_attributes()
        for field in required_attrs:
            if not hasattr(self, field) or not getattr(self, field):
                raise exceptions.InvalidObjectSourceError(f"blob attribute {field} can not be null")

    @abc.abstractmethod
    def initialize(self, data: Any, url_object: StorageURL):
        """assign all attributes here, subclass must override

        Parameters
        ----------
        data: Any
            GcsBlob, S3Object, S3ObjectSummary, dict etc.
        url_object: StorageURL
            we need this to be able to stitch together the full url for the object

        Returns
        -------

        """
        raise NotImplementedError

    def get_hash(self) -> tuple:
        """returns the hash for the blob object

        Returns
        -------
        tuple:
            (hash_type, hash_value)
        """
        self.hashes = self.hashes or {}
        for hash_type in self.get_hash_preferences():
            if hash_type in self.hashes:
                return hash_type, self.hashes[hash_type]

        hash_type, hash_value = self.compute_hash()
        # verify
        if not hash_type or not hash_value:
            raise exceptions.InvalidObjectSourceError("hash_type and hash_value are both required")
        return self.validate_hash(hashes={hash_type: hash_value})

    def validate_hash(self, hashes: dict) -> tuple:
        """validates the blob's hash

        Parameters
        ----------
        hashes: dict
            {hash_type: hash_value}

        Returns
        -------
        tuple:
            (hash_type, hash_value) - validated
        """
        hash_prefs: list = self.get_hash_preferences()
        # order the hashes based on preferences
        ordered_hashes = []
        for hash_type in hash_prefs:
            if hash_type in hashes:
                ordered_hashes.append((hash_type, hashes[hash_type]))

        if not ordered_hashes:
            raise exceptions.InvalidObjectSourceError(f"invalid hash_type, allowed hashes are: {','.join(hash_prefs)}")
        # return the more preferred item
        return ordered_hashes[0]

    def compute_hash(self) -> tuple:
        """calculate and return hash
        subclass to implement

        Returns
        -------
        tuple:
            (hash_type, hash_value)

        """
        raise NotImplementedError

    def get_hash_preferences(self) -> list:
        # order of preferences for hash_type, subclass can override
        return ["md5", "crc32", "crc32c", "sha256", "sha1"]

    def compare_hash(self, other: StorageData) -> bool:
        """compare hashes of two blobs

        Parameters
        ----------
        other: StorageData
            other blob

        Returns
        -------
        bool:
            True if the blobs have same hashes, False otherwise
        """
        hash_type, hash_value = self.get_hash()
        # Look for the same hash_type in the other blob
        if hash_type in other.hashes:
            return hash_value == other.hashes[hash_type]
        return False

    def to_dict(self) -> dict:
        """Used in the server to serialize the object."""
        return {
            "url": self.url,
            "host": self.host,
            "name": self.name,
            "size": self.size,
            "content_type": self.content_type,
            "hashes": self.hashes,
            "path_in_asset": self.path_in_asset
        }
