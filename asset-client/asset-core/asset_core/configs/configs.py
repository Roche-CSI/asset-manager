from __future__ import annotations

from asset_utils.utils.log_utils import LoggingMixin
from .auth_config import AuthConfig
from .client_configs import SettingsConfig, AssetConfig, AssetsHomeConfig
from .config_modes import ConfigModes
from .remote_config import RemoteConfig
from .server_config import ServerConfig

DOCS = {
    "URL": "GITHUB_PAGES_URL",
    "GITHUB": "GIT_REPO_URL",
    "ISSUE": "DASHBOARD_ISSUE_PAGE_URL"
}

"""CHANGE TO SANDBOX / PRODUCTION WHEN deploying"""
DEFAULT_MODE = ConfigModes.USER_TEST


class Configs(LoggingMixin):
    modes = ConfigModes

    remote: RemoteConfig = None
    asset: AssetConfig = None
    asset_home: AssetsHomeConfig = None
    settings: SettingsConfig = None
    server: ServerConfig = None
    auth: AuthConfig = None

    DOCS: dict = None
    MODE: str = None  # TEST, DEV, PRODUCTION

    _instance = None

    def __init__(self):
        raise RuntimeError('Call initialize() instead')

    @property
    def docs_url(self):
        return self.DOCS["URL"]

    @staticmethod
    def shared(mode: ConfigModes = None):
        mode = mode or DEFAULT_MODE
        if not Configs._instance:
            Configs._instance = Configs._initialize(mode=mode)
        return Configs._instance

    @classmethod
    def _initialize(cls, mode: ConfigModes):
        config_class = cls.config_class(mode=mode)
        instance = config_class.__new__(config_class)
        instance.post_init(mode=mode)
        return instance

    @classmethod
    def config_class(cls, mode: ConfigModes):
        if mode == ConfigModes.DEV:
            return DevConfigs
        elif mode == ConfigModes.UNIT_TEST:
            return UnitTestConfigs
        # elif mode == ConfigModes.SANDBOX:
        #     return SandboxConfigs
        elif mode == ConfigModes.PRODUCTION:
            return ProdConfigs
        else:
            return UserTestConfigs

    def post_init(self, mode: ConfigModes):
        self.server = ServerConfig(mode=mode)
        self.auth = AuthConfig(mode=mode)
        self.remote = RemoteConfig()
        self.asset = AssetConfig()
        self.asset_home = AssetsHomeConfig(mode=mode)
        self.settings = SettingsConfig()
        self.DOCS = DOCS

    @classmethod
    def de_init(cls):
        cls._instance = None


"""
declare all project specific settings here
"""


class ProdConfigs(Configs):
    MODE = 'PRODUCTION'


class DevConfigs(Configs):
    MODE = 'DEV'


# class SandboxConfigs(Configs):
#     MODE = 'SANDBOX'


class UserTestConfigs(Configs):
    MODE = 'USER_TEST'


class UnitTestConfigs(Configs):
    MODE = 'UNIT_TEST'
