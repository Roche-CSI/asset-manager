from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction, CliOption


class AuthLogin(CliAction):
    name = "login"
    help_msg = "Signing into asset-manager"
    requires_repo = False
    requires_store = False
    requires_auth = False

    def run(self, args):
        self.user_log.message("signing into asset-manager...")
        SettingsAPI().user_login(token=args.token)

    def get_options(self):
        return [
            CliOption(
                dest="token",
                short_name="t",
                full_name="token",
                n_args="?",
                help_msg="login with a token returned by the server",
            ),
        ]
