from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction, CliOption


class AuthSignup(CliAction):
    name = "signup"
    help_msg = "Signing up with asset-manager"
    requires_repo = False
    requires_store = False
    requires_auth = False

    def run(self, args):
        SettingsAPI().user_signup(username=args.username, email=args.email)

    def get_options(self):
        """allow token based login for cloud login since oauth2 flow won't work in cloud pipelines"""
        return [
            CliOption(
                dest="username",
                short_name="u",
                full_name="user",
                n_args="?",
                help_msg="username",
            ),
            CliOption(
                dest="email",
                short_name="e",
                full_name="email",
                n_args="?",
                help_msg="email",
            ),

        ]
