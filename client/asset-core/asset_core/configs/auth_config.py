import os

from asset_core.configs.config_modes import ConfigModes
from asset_core.configs.server_config import DEV_URL, PROD_URL, UNIT_TEST_URL, USER_TEST_URL


class AuthConfig:

    def __init__(self, mode: ConfigModes):
        self._mode = mode

    @property
    def server_url(self):
        # allow for user to override using the environment variable directly, we need this for different deployments
        auth_url = os.getenv("ASSET_AUTH_SERVER_URL")
        if auth_url:
            return auth_url

        # fallback to asset-url since both and asset and auth services are same for the time-being
        asset_url = os.getenv("ASSET_SERVER_URL")
        if asset_url:
            return asset_url

        url = DEV_URL  # default to dev
        if self._mode == ConfigModes.PRODUCTION:
            url = PROD_URL
        elif self._mode == ConfigModes.USER_TEST:
            url = USER_TEST_URL
        elif self._mode == ConfigModes.UNIT_TEST:
            url = UNIT_TEST_URL

        # check if we need to skip dns resolution
        dns_override = os.getenv("ASSET_SERVER_SKIP_DNS")
        if dns_override and dns_override == "true":
            return url.get("ip")

        return url.get("host")

    @property
    def routes(self):
        return {
            "auth": "auth/cli/google_auth",
            "auth_url": "auth/cli/google_auth_url",
            "login": "auth/cli/login",
            "token_login": "auth/cli/token_login",
            "response_login": "auth/cli/response_login",
            "signup": "auth/cli/signup"
        }

    @property
    def ssl_verify(self):
        return False

    @property
    def auth_route(self):
        return self.routes["auth"]

    @property
    def auth_url_route(self):
        return self.routes["auth_url"]

    @property
    def email_login_route(self):
        return self.routes["login"]

    @property
    def token_login_route(self):
        return self.routes["token_login"]

    @property
    def response_login_route(self):
        return self.routes["response_login"]

    @property
    def user_signup_route(self):
        return self.routes["signup"]
