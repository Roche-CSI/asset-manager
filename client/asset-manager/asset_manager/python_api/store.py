from functools import cached_property

from asset_core.api.settings_api import SettingsAPI


class Store(object):

    @cached_property
    def _api(self) -> SettingsAPI:
        """Instance of SettingsAPI."""
        return SettingsAPI()

    def info(self) -> dict:
        """Retrieves information about the asset store.

        Returns
        -------
        dict
            A dictionary containing information about the asset store
        """
        return self._api.asset_home_info(jsonize=True)

    def clear(self, confirm: bool = False):
        """Clears the asset store."""
        return self._api.remove_asset_home(confirm=confirm)

    def prune(self):
        """Remove invalid assets from the asset store."""
        return self._api.prune_asset_store()

    def set(self, target: str):
        """Sets the asset store location.

        Parameters
        ----------
        target : str
            The path to set as the asset store
        """
        return self._api.set_asset_home(dst_dir=target)
