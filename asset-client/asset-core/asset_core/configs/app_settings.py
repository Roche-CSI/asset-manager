from __future__ import annotations

import contextlib
import copy
import os
import re
from importlib.metadata import version, PackageNotFoundError

from asset_core.configs.configs import Configs
from asset_core.configs.user_settings import UserSettings
from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_pluggy.storage.storage_factory import StorageFactory
from asset_utils.common import exceptions
from asset_utils.utils import utils
from asset_utils.utils.file_utils import FileUtils

SETTINGS_DIR = ".asset-manager"  # asset manager metadata
SETTINGS_FILE = "globals.json"  # i.e. user, project etc


class AppSettings:
    # config = None
    _instance = None

    @staticmethod
    def shared() -> AppSettings:
        if not AppSettings._instance:
            AppSettings._instance = AppSettings._initialize()
        return AppSettings._instance

    @classmethod
    def _initialize(cls):
        obj: AppSettings = cls.__new__(cls)
        obj._post_init()
        return obj

    def _post_init(self):
        self.set_assets_home()
        # max concurrent files open
        FileUtils.set_max_concurrent_files(num_files=self.max_concurrent_files_limit)

    def __init__(self):
        raise RuntimeError('Call shared() instead')

    def __repr__(self):
        return self.settings_file

    def set_assets_home(self):
        """assets_home is where .assets directory will be located"""
        # ASSET_HOME is the location of asset store
        if not self.assets_home:
            self.assets_home = os.getenv("ASSET_HOME") or self.default_home_dir

    @property
    def cli_version(self):
        # needed by server to validate breaking changes for new releases
        try:
            # check for asset-manager first then asset-sandbox
            ver = version('asset-manager')
        except PackageNotFoundError:
            try:
                ver = version('asset-sandbox')
            except PackageNotFoundError as e:
                # if neither is found, then raise an exception
                raise exceptions.AssetException(f"cli version not found: {e}")

        return self.extract_version(ver)

    def extract_version(self, string):
        # Get rid of .dev from the version string
        pattern = r'^\d+\.\d+\.\d+'
        match = re.match(pattern, string)

        if match:
            return match.group(0)
        return None

    @property
    def settings_dir(self):
        """ASSET_ROOT
         - is where the asset-manager settings are stored i.e  .asset-manager/globals.yaml
         - allow override such that test environment is isolated from dev/sandbox/prod
        """
        return os.path.join(os.getenv("ASSET_ROOT") or self.default_home_dir, SETTINGS_DIR)

    @property
    def settings_file(self):
        path = os.path.join(self.settings_dir, SETTINGS_FILE)
        FileUtils.create_file_if_not_exists(path=path)
        return path

    @property
    def default_home_dir(self):
        return utils.user_home_dir()

    @property
    def data(self) -> dict:
        try:
            return self._data
        except AttributeError:
            if os.path.exists(self.settings_file):
                self._data = FileUtils.read_json(self.settings_file)
            self._data = self._data or {}
            return self._data

    @data.setter
    def data(self, x):
        self._data = x
        FileUtils.write_json(data=self._data, abs_path=self.settings_file)

    @property
    def assets_home(self) -> str:
        try:
            return self._assets_home
        except AttributeError:
            # we do environment override for ASSET_HOME in read
            # this way, the user has the option to temporarily switch to a new store
            # without affecting the permanent asset store
            # self._assets_home = os.getenv('ASSET_HOME') or self.data.get('assets_home')
            self._assets_home = self.data.get('assets_home')
            return self._assets_home

    @assets_home.setter
    def assets_home(self, x):
        self._assets_home = x
        self.data = utils.update_dict(self.data, {'assets_home': x})

    @property
    def max_concurrent_files_limit(self):
        return FileUtils.max_concurrent_files_limit()

    @property
    def user(self) -> dict:
        try:
            return self._user
        except AttributeError:
            # default to machine user id
            self._user = self.data.get('user')  # or get_user_id()
            return self._user

    @user.setter
    def user(self, x):
        self._user = x
        # set to null to avoid data structure conflicts
        self.data = utils.update_dict(self.data, {'user': None})
        self.data = utils.update_dict(self.data, {'user': self._user})

    @contextlib.contextmanager
    def project_environment(self, project_id: str):
        # credentials and url
        self.set_project_environment(project_id=project_id)
        yield
        # clean up
        self.unset_project_environment()

    def set_project_environment(self, project_id):
        # keep a copy of the previous environment
        self._prev_environs = getattr(self, "_prev_environs", [])
        self._prev_environs.append(copy.deepcopy(dict(os.environ)))
        # pop any existing credentials
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

        if project_id not in self.projects:
            raise exceptions.InvalidProjectError(msg=f"invalid project: {project_id}, project not found")

        project = self.projects.get(project_id)
        os.environ["ASSET_PROJECT_ID"] = project_id
        # todo: move to tokens instead of service_account.json
        # allow for user override i.e. to tackle issues such as not having access to genia bucket
        # todo: discuss and resolve

        # set the credentials from the project
        credentials_project = project.get("credentials_user")
        StorageCredentials.shared().set_credentials(cred=credentials_project)
        StorageCredentials.shared().set_content_credentials(cred=credentials_project)

        # user provides an overriding credentials
        user_credentials = os.environ.get("ASSET_CREDENTIALS")
        if user_credentials and os.path.exists(user_credentials):
            credentials = FileUtils.read_json(user_credentials)
            StorageCredentials.shared().set_content_credentials(cred=credentials)

        os.environ["ASSET_STAGING_URL"] = project.get("staging_url")
        os.environ["ASSET_REMOTE_URL"] = project.get("remote_url")
        storage = StorageFactory.storage_for_url(src_url=project.get("remote_url"))
        os.environ["ASSET_PROJECT_STORAGE_ID"] = storage.name
        os.environ["ASSET_USER"] = self.user.get("username")
        # user configs
        self.user_configs.activate()
        self.set_plugin_env()

    def unset_project_environment(self):
        os.environ.pop("ASSET_PROJECT_ID", None)
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        os.environ.pop("ASSET_STAGING_URL", None)
        os.environ.pop("ASSET_REMOTE_URL", None)
        os.environ.pop("ASSET_PROJECT_STORAGE_ID", None)
        os.environ.pop("ASSET_USER", None)
        self.user_configs.deactivate()
        self.unset_plugin_env()
        # pop and restore previous environment
        self._prev_environs = getattr(self, "_prev_environs", [])
        if self._prev_environs:
            os.environ.update(self._prev_environs.pop())

    def set_plugin_env(self):
        """sets the necessary environment variables for the plugins to work
        """
        if not os.getenv("ASSET_SERVER_URL", None):
            os.environ["ASSET_SERVER_URL"] = Configs.shared().server.server_url

    def unset_plugin_env(self):
        """unsets the necessary environment variables for the plugins
        """
        os.environ.pop("ASSET_SERVER_URL", None)

    def storage_url(self, staging=False):
        # allow for dev overrides
        url = os.getenv("ASSET_STAGING_URL" if staging else "ASSET_REMOTE_URL")
        if not url:
            raise exceptions.InvalidRemoteURLError()
        return url

    @property
    def default_project(self):
        try:
            return self._default_project
        except AttributeError:
            # default to machine user id
            self._default_project = self.data.get('default_project')  # or get_user_id()
            return self._default_project

    @default_project.setter
    def default_project(self, x: str):
        self._default_project = x
        self.data = utils.update_dict(self.data, {'default_project': self._default_project})

    def set_roles(self, roles: list, append: bool = True):
        """translates roles into project and access type
        and saves to settings db
        Parameters
        ----------
        roles
        append: bool
                if true, then we add to existing roles else, we replace any existing roles data
        Returns
        -------
        """
        # the same project might exist in multiple roles, so here we aggregate
        # all the roles for a project
        projects = {}
        for role in roles:
            project: dict = role.get("project")
            project_id = project["id"]
            project["can_edit"] = bool(role.get("can_edit") or projects.get(project_id, {}).get("can_edit"))
            project["can_read"] = bool(role.get("can_read") or projects.get(project_id, {}).get("can_read"))
            project["can_delete"] = bool(role.get("can_delete") or projects.get(project_id, {}).get("can_delete"))
            project["can_admin_project"] = bool(role.get("can_admin_project") or
                                                projects.get(project_id, {}).get("can_admin_project"))
            projects[project_id] = project

        if not append:
            # do a clean-up of previous roles
            self.projects = None
        self.projects = projects

        # if there is one project, then we set it as active
        project_ids = list(self.projects.keys())
        if len(project_ids) == 1:
            self.active_project = project_ids[0]
        else:
            # exclude default project
            if self.default_project:
                project_ids.remove(self.default_project)
            self.active_project = project_ids[0]

    def clear_user_data(self):
        self.data = utils.update_dict(self.data,
                                      {
                                          'projects': None,
                                          'auth': None,
                                          'active_project': None,
                                          'user': None,
                                          'default_project': None
                                      })
        # delete credential files
        credential_files = utils.list_files(root_dir=self.settings_dir, pattern="credential_*.json")
        for file in credential_files:
            os.unlink(file)

    @property
    def projects(self) -> dict:
        try:
            return self._projects
        except AttributeError:
            self._projects = self.data.get('projects') or {}  # default is empty dict
            return self._projects

    @projects.setter
    def projects(self, x: dict):
        self._projects = x
        self.data = utils.update_dict(self.data, {'projects': self._projects})

    @property
    def active_project(self) -> str:
        try:
            return self._active_project
        except AttributeError:
            self._active_project = self.data.get('active_project') or None  # default is null
            return self._active_project

    @active_project.setter
    def active_project(self, x: str):
        self._active_project = x
        self.data = utils.update_dict(self.data, {'active_project': self._active_project})

    @property
    def active_project_data(self) -> dict:
        return self.projects.get(self.active_project)

    @property
    def user_configs(self) -> UserSettings:
        try:
            return self._user_configs
        except AttributeError:
            # self._user_configs = self.data.get('user_configs') or {}  # default is null
            self._user_configs = UserSettings(app_settings=self)
            return self._user_configs

    @property
    def user_prompt(self):
        try:
            return self._user_prompt
        except AttributeError:
            self._user_prompt = self.data.get('user_prompt') or True  # default is true
            return self._user_prompt

    @user_prompt.setter
    def user_prompt(self, x):
        self._user_prompt = x
        self.data = utils.update_dict(self.data, {'user_prompt': self._auth})

    @classmethod
    def validate(cls, data: dict):
        required = ["active_project", "auth", "user", "projects"]
        missing = []
        for field in required:
            if not data.get(field, None):
                missing.append(field)
        if missing:
            raise Exception("missing required fields:{}".format(",".join(missing)))

        project = data.get("projects").get(data.get("active_project"))
        if not project:
            raise Exception("project data is missing")

        if not project.get("staging_url") or not project.get("remote_url"):
            raise Exception("asset environment needs a valid staging_url and remote_url")

        if not project.get("credentials_user"):
            raise Exception("credential_user is required for the project")

        return data
