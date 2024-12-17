import os

from asset_core.configs.config_modes import ConfigModes

DEV_URL = {
    "host": "http://localhost:5000",
    "ip": "http://127.0.0.1:5000"
}

PROD_URL = {
    "host": "PROD_SERVER_URL",
    "ip": "PROD_SERVER_IP"
}

USER_TEST_URL = {
    "host": "SANBOX_SERVER_URL",
    "ip": "SANDBOX_SERVER_IP"
}


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
            url = PROD_URL
        elif self._mode == ConfigModes.USER_TEST:
            url = USER_TEST_URL
        # check if we need to skip dns resolution
        dns_override = os.getenv("ASSET_SERVER_SKIP_DNS")
        if dns_override and dns_override == "true":
            return url["ip"]

        return url["host"]

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
            "find_ref": "asset_ref/find",
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
