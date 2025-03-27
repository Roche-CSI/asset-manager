import logging

from asset_db.db import Database

logger = logging.getLogger(__name__)


class RepoDB(Database):
    """
    Stores Assets Meta information
    """
    type = "repo-db"

    def add(self, **kwargs):
        """Adds to existing list of objects"""
        self.update(**kwargs)

    def get(self, key) -> dict:
        """Returns objects from yaml file"""
        return self.retrieve(key=key)

    def remove(self, keys: list):
        """Deletes specific assets from the list

        Parameters
        ----------
        keys : list
            asset ids
        """
        data = self.data()
        for id in keys:
            deleted = data.pop(id, None)
            if deleted:
                pass
                # logger.info("asset {} removed.".format(id))
            else:
                logger.info("asset not added yet, ignoring remove for:{}".format(id))
        self._write_to_file(data)

    def clear(self):
        """Clears all assets"""
        self._write_to_file(data={})
