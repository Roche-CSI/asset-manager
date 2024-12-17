from functools import cached_property

from asset_core.api.settings_api import SettingsAPI


class Project(object):

    @cached_property
    def _api(self) -> SettingsAPI:
        """A cached property that returns an instance of SettingsAPI.

        Returns
        -------
        SettingsAPI
            An instance of SettingsAPI for interacting with project settings.
        """
        return SettingsAPI()

    @cached_property
    def active(self) -> str:
        """Retrieves the name of the currently active project.

        Returns
        -------
        str
            The name of the active project.
        """
        return self._api.print_active_project(jsonize=True)

    def list(self) -> list:
        """Lists all projects available to the user.

        Returns
        -------
        list
            A list of all projects.
        """
        return self._api.print_all_projects(jsonize=True)

    def activate(self, project_name: str) -> bool:
        """Activates a given project by name.

        Parameters
        ----------
        project_name : str
            The name of the project to activate.

        Returns
        -------
        bool
            True if the project was successfully activated, False otherwise.
        """
        return self._api.set_active_project(project_name=project_name)
