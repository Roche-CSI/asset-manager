import logging
import os

from asset_db.db import Database

logger = logging.getLogger(__name__)


class StatesDB(Database):
    """Stats db that holds file information to manage
    Important: States db is asset-specific
    """

    type = "asset-states"

    def set_asset_state(self, state):
        self.update(**{"asset_state": state})

    def get_asset_state(self):
        return self.retrieve("asset_state") or None

    def get_ref_states(self):
        return self.retrieve("ref_states") or {}

    def set_commit_message(self, x):
        self.update(**{"commit_message": x})

    def get_commit_message(self):
        return self.retrieve("commit_message")

    def add_object_states(self, **kwargs):
        """Adds to existing list of stats

        Parameters
        ----------
        kwargs : dict
            key:value pairs of id: state
        """
        self.update(**{"object_states": kwargs})

    def add_refs_states(self, **kwargs):
        """Adds to existing list of stats

        Parameters
        ----------
        kwargs : dict
            key:value pairs of id: state
        """
        self.update(**{"ref_states": kwargs})

    def get_object_states(self) -> dict:
        """Returns assets and their md5 hashes"""
        return self.retrieve("object_states") or {}

    def get_content_states(self) -> dict:
        return self.retrieve("content_states") or {}

    def add_content_states(self, **kwargs):
        self.update(**{"content_states": kwargs})

    def remove_content_states(self, ids: list):
        data = self.data()
        states = data.get("content_states", {})
        for id in ids:
            deleted = states.pop(id, None)
            if deleted:
                pass
                # logger.info("asset {} removed.".format(id))
            else:
                logger.warning("content not added yet, ignoring remove for:{}".format(id))

        data["content_states"] = states
        self._write_to_file(data=data)

    def remove_object_states(self, ids: list):
        """Deletes specific assets from the list

        Parameters
        ----------
        ids : list
            url ids of asset objects
        """
        data = self.data()
        states = data.get("object_states", {})
        for id in ids:
            deleted = states.pop(id, None)
            if deleted:
                pass
                # logger.info("asset {} removed.".format(id))
            else:
                logger.warning("asset not added yet, ignoring remove for:{}".format(id))

        data["object_states"] = states
        self._write_to_file(data=data)

    def remove_ref_states(self, keys: list):
        """Deletes specific assets_refs from the list

        Parameters
        ----------
        keys : list
            asset ids
        """
        data = self.data()
        states = data.get("ref_states", {})
        for key in keys:
            _ = states.pop(key, None)

        data["ref_states"] = states
        self._write_to_file(data=data)

    def data(self):
        if not os.path.exists(self.path):
            # nothing stored yet
            return {"object_states": {}, "asset_state": None}
        return self._read_from_file() or {}
