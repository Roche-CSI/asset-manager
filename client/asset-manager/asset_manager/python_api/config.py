from functools import cached_property
from typing import Any

from asset_core.api.settings_api import SettingsAPI


class Config(object):

    @cached_property
    def _api(self) -> SettingsAPI:
        """Instance of SettingsAPI."""
        return SettingsAPI()

    def info(self) -> dict:
        """Retrieves information about the current configuration.

        Returns
        -------
        dict
            A dictionary containing configuration options for the user.
        """
        return self._api.print_user_configs(jsonize=True)

    def set(self, key: str, value: Any):
        """Sets custom configuration options.

        Parameters
        ----------
        key : str
            The key for the configuration option.
        value : Any
            The value for the configuration option.
        """
        return self._api.set_user_configs({key: value})

    def reset(self, *keys):
        """Resets the configuration to the default value.

        Parameters
        ----------
        keys : str
            The keys to reset.
        """
        return self._api.reset_user_configs(keys=keys)
