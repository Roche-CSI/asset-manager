from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction, CliOption


class SetConfigs(CliAction):
    name = "set"
    help_msg = "Set custom configuration options"
    requires_repo = False
    requires_store = False
    requires_auth = False

    def run(self, args):
        SettingsAPI().set_user_configs({args.key: args.value})

    def get_options(self):
        return [
            CliOption(
                dest="key",
                short_name="k",
                full_name="key",
                n_args="?",
                help_msg="config key",
            ),
            CliOption(
                dest="value",
                short_name="v",
                full_name="value",
                n_args="?",
                help_msg="config value",
            ),
        ]
