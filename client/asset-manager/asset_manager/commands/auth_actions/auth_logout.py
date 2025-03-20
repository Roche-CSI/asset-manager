from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction


class AuthLogout(CliAction):
    name = "logout"
    help_msg = "logs out from asset-manager"
    requires_store = False
    requires_repo = False
    requires_auth = False

    def run(self, args):
        SettingsAPI().user_logout()

    def get_options(self):
        return []
