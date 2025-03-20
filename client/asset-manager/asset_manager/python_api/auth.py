from functools import cached_property

from asset_core.api.settings_api import SettingsAPI
from asset_utils.common import exceptions


class Auth(object):

    @cached_property
    def _api(self) -> SettingsAPI:
        """A cached property that returns an instance of SettingsAPI.

        Returns
        -------
        SettingsAPI
            An instance of SettingsAPI for interacting with auth settings.
        """
        return SettingsAPI()

    def info(self, token=False) -> dict:
        """Retrieves information about the current user.

        Parameters
        ----------
        token : bool, optional
            If True, includes the authentication token in the returned information, by default False.

        Returns
        -------
        dict
            A dictionary containing information about the current user. If `token` is True, this will
            also include the user's authentication token.
        """
        auth_info = self._api.print_auth(jsonize=True)
        if token:
            auth_info.update(self._api.print_auth_token(jsonize=True))
        return auth_info

    def login(self, token: str = None) -> dict:
        """Logs in a user to the asset manager.

        Parameters
        ----------
        token : str, optional
            The authentication token for the user. If not provided, standard authentication flow is used.

        Returns
        -------
        dict
            A dictionary containing the result of the login operation, including any user information.
        """
        return self._api.user_login(token=token, jsonize=True)

    def logout(self):
        """Logs out the current user from the asset manager.

        This method does not return any value.
        """
        self._api.user_logout()

    def update(self):
        """Update user credentials for any new project access etc.

        This method is deprecated and will raise an exception if called.

        Raises
        ------
        AssetException
            Always raised to indicate the method is deprecated and should not be used.
        """
        raise exceptions.AssetException("deprecated. Use login() instead")
