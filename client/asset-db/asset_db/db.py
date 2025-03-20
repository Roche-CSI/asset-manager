import logging
import os
from typing import List, AnyStr, Union

from asset_utils.utils import utils
from asset_utils.utils.file_utils import FileUtils

logger = logging.getLogger(__name__)

DB_FILE = "json"  # yaml


class Database:
    """Yaml wrapper to present a db like interface for writing to yaml files.
    Singleton, so make sure all DBs inherit directly from this class only
    Subclasses also behave as singletons
    """
    path = None
    backup_path = None  # in case we want to cache the database
    _persisted_data = {}
    _instances = {}

    def __new__(cls, *args, **kwargs):
        path = kwargs.get('path') or args[0]  # there can be only one instance per path
        if not path:
            raise Exception("required param: path is null")

        if cls._instances.get(path, None) is None:
            cls._instances[path] = super(Database, cls).__new__(cls)

        if cls._instances[path].__class__.__name__ != cls.__name__:
            raise Exception("Instance already exists with same path but different class type")
        return cls._instances[path]

    def __init__(self, path, backup_path: str = None):
        if path:
            FileUtils.create_file_if_not_exists(path)
        self.path = path
        self.backup_path = backup_path
        # create backup through hardlink
        if self.backup_path:
            if not os.path.exists(self.backup_path):
                FileUtils.create_file_if_not_exists(self.backup_path)
                if not os.path.samefile(self.path, self.backup_path):
                    try:
                        os.unlink(self.backup_path)  # delete existing
                        os.link(src=self.path, dst=self.backup_path)
                    except OSError as e:
                        logger.warning(f"Backup not enabled because of OSError: {str(e)}")

    def copy_to(self, db):
        db.update(**self.data())

    def update(self, **kwargs):
        data = self.data() or {}
        data = utils.update_dict(data, kwargs)
        self._write_to_file(data=data)
        return data

    def _write_to_file(self, data):
        """Stores the dictionary in a json file, overwrites existing data"""
        self._persisted_data = data
        self.__class__.write(data=self._persisted_data, path=self.path)

    @classmethod
    def write(cls, data, path):
        if DB_FILE == "yaml":
            FileUtils.write_yaml(abs_path=path, data=data)
        elif DB_FILE == "json":
            FileUtils.write_json(abs_path=path, data=data, sort_keys=False)
        else:
            raise Exception("Unsupported DB format")

    def _read_from_file(self):
        """returns data from yaml file"""
        self._persisted_data = self._persisted_data or self.__class__.read(self.path)
        return self._persisted_data

    @classmethod
    def read(cls, path):
        if not path or not os.path.exists(path):
            # nothing stored yet
            return {}
        if DB_FILE == "json":
            return FileUtils.read_json(abs_path=path) or {}
        elif DB_FILE == "yaml":
            return FileUtils.read_yaml(abs_path=path) or {}
        else:
            raise Exception("Unsupported DB format")

    def retrieve(self, key: Union[AnyStr, List]):
        """Retrieves specific values for specific keys from the json file.
           If keys are not found, the default value of None is returned.
        """
        data = self.data()
        if isinstance(key, str):
            return data.get(key, None)
        elif isinstance(key, list):
            result = {}
            for each_key in key:
                result[each_key] = data.get(each_key, None)
            return result
        else:
            return None

    def data(self):
        return self._read_from_file()
