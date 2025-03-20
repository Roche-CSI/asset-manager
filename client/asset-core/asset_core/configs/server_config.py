import os

from asset_core.configs.config_modes import ConfigModes
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands

DEV_URL = {
    "host": "http://localhost:5000",
    "ip": "http://127.0.0.1:5000"
}

UNIT_TEST_URL = {
    "host": "http://localhost:8000",
    "ip": "http://127.0.0.1:8000"
}

PROD_URL = {}

USER_TEST_URL = {}


class ServerConfig:

    def __init__(self, mode: ConfigModes):
        self._mode = mode

    @property
    def server_url(self):
        # allow for user to override using the environment variable directly, we need this for different deployments
        asset_server_url = os.getenv("ASSET_SERVER_URL")
        if asset_server_url:
            return asset_server_url

        url = DEV_URL
        if self._mode == ConfigModes.PRODUCTION:
            if not PROD_URL:
                e = exceptions.ServerUrlNotSetError()
                e.logs.add("please set the 'server_url' using asset config set")
                e.logs.add(UserCommands().set_user_configs())
                raise e
            url = PROD_URL
        elif self._mode == ConfigModes.USER_TEST:
            if not USER_TEST_URL:
                e = exceptions.ServerUrlNotSetError()
                e.logs.add("please set the 'server_url' using asset config set")
                e.logs.add(UserCommands().set_user_configs())
                raise e
            url = USER_TEST_URL
        elif self._mode == ConfigModes.UNIT_TEST:
            url = UNIT_TEST_URL

        # check if we need to skip dns resolution
        dns_override = os.getenv("ASSET_SERVER_SKIP_DNS")
        if dns_override and dns_override == "true":
            return url.get("ip")

        return url.get("host")

    @property
    def ssl_verify(self):
        return False

    @property
    def routes(self):
        return {
            "asset": "asset",
            "asset_class": "asset_class",
            "asset_commit": "asset_commit",
            "asset_version": "asset_version",
            "find_version": "asset_version/find",
            "asset_ref": "asset_ref",
            "find_ref": "asset_ref/find"
        }

    @property
    def asset_route(self):
        return self.routes["asset"]

    @property
    def asset_class_route(self):
        return self.routes["asset_class"]

    @property
    def asset_commit_route(self):
        return self.routes["asset_commit"]

    @property
    def asset_version_route(self):
        return self.routes["asset_version"]

    @property
    def find_version_route(self):
        return self.routes["find_version"]

    @property
    def asset_ref_route(self):
        return self.routes["asset_ref"]

    @property
    def find_ref_route(self):
        return self.routes["find_ref"]

    @property
    def issue_url(self):
        return os.path.join(self.server_url, "issue")
