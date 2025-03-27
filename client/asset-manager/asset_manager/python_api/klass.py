from asset_core.api.store_api.class_info import ClassInfoAPI
from asset_core.api.store_api.fetch import FetchAPI
from asset_core.api.store_api.list import ListAPI
from asset_core.store import AssetStore


class Klass(object):

    def __init__(self):
        """Initializes a new instance of the Klass class.
        """
        self._store = AssetStore.shared(create_if_not_exists=True)

    def fetch(self):
        """Fetches class list from the asset server, updating local cache.

        This method does not return any value.
        """
        api = FetchAPI(store=self._store)
        with api.environment():
            api.fetch_classes()

    def info(self, class_name: str) -> dict:
        """Retrieves information about a specific class by its name.

        Parameters
        ----------
        class_name : str
            The name of the class for which information is requested.

        Returns
        -------
        dict
            A dictionary containing information about the class.
        """
        api = ClassInfoAPI(store=self._store)
        with api.environment():
            return api.print_class_info(class_name, jsonize=True)

    def list(self) -> list:
        """Lists all classes available in the asset manager.

        Returns
        -------
        list
            A list of all classes.
        """
        api = ListAPI(store=self._store)
        with api.environment():
            return api.list_classes(jsonize=True)
