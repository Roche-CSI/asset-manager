import logging

from asset_db.db import Database
from asset_utils.utils import utils

logger = logging.getLogger(__name__)


class ManifestDB(Database):
    """
    Class for managing asset manifest databases.
    """
    type = "asset-manifest"

    def add_objects(self, **kwargs) -> None:
        """Adds a new object to the manifest database.

        Parameters
        ----------
        **kwargs : dict
            Key-value pairs to be added as objects to the database.
        """
        data = {"objects": kwargs}
        self.update(**data)

    def get_objects(self) -> dict:
        """Retrieves all objects from the manifest database.

        Returns
        -------
        dict
            A dictionary of all objects in the manifest database.
        """
        return self.retrieve("objects")

    def get(self, key):
        """Retrieves a specific value from the manifest database based on the provided key.

        Parameters
        ----------
        key : str
            The key for the value to be retrieved.

        Returns
        -------
        The value associated with the key, if found; otherwise, None.
        """
        return self.data().get(key)

    def remove_objects(self, ids: list) -> None:
        """Removes specified objects from the manifest database.

        Parameters
        ----------
        ids : list
            A list of ids representing the objects to be removed.

        Returns
        -------
        None
        """
        data = self.data()
        objects = data.get("objects")
        for _id in ids:
            deleted = objects.pop(_id, None)
            if deleted:
                pass
            else:
                logger.info("asset not added yet, ignoring remove for:{}".format(_id))
        data["objects"] = objects
        self._write_to_file(data)

    def clear_objects(self) -> None:
        """Clears all objects from the manifest database.

        Returns
        -------
        None
        """
        data = self.data()
        data["objects"] = {}
        self._write_to_file(data=data)

    def get_version(self) -> str:
        """Retrieves the version of the asset from the manifest database.

        Returns
        -------
        str
            The version of the asset.
        """
        return self.retrieve("version")

    def set_version(self, version) -> None:
        """Sets the version of the asset in the manifest database.

        Parameters
        ----------
        version : str
            The version to be set for the asset.

        Returns
        -------
        None
        """
        data = {
            "version": version,
            "user": utils.get_user_id(),
            "time": utils.get_time_stamp()
        }
        self.update(**data)

    def get_parent_version(self):
        return self.retrieve("parent_version")

    def set_parent_version(self, version):
        data = {"parent_version": version}
        self.update(**data)
