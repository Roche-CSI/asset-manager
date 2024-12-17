import logging

from asset_db.db import Database

logger = logging.getLogger(__name__)


class AssetsDB(Database):
    """
    Stores the md5 hashes of asset*.yamls. We use this to check which
    files need to be re-downloaded during fetch operations
    """
    type = "assets-db"

    @property
    def file_hashes(self):
        try:
            return self._file_hashes
        except AttributeError:
            self._file_hashes = self.data()
            return self._file_hashes

    def add_file_hash(self, path, hash):
        """Adds to existing list of files"""
        updated = self.update(**{path: hash})
        setattr(self, "_file_hashes", updated)

    def remove_files(self, *paths):
        """Deletes specific assets from the list"""
        data = self.file_hashes
        for path in paths:
            deleted = data.pop(path, None)
            if deleted:
                pass
                # logger.info("file {} removed.".format(id))
            else:
                logger.info("file not added yet, ignoring remove for:{}".format(id))
        setattr(self, "_file_hashes", data)
        self._write_to_file(data)

    def clear(self):
        """Clears all assets"""
        setattr(self, "_file_hashes", {})
        self._write_to_file(data={})
