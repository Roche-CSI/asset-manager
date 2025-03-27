from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction


class AuthUpdate(CliAction):
    name = "update"
    help_msg = "Update asset-manager credentials"
    requires_repo = False
    requires_store = False
    requires_auth = True

    def run(self, args):
        self.user_log.message("updating asset-credentials from server")
        SettingsAPI().auth_update()

    def get_options(self):
        return []
