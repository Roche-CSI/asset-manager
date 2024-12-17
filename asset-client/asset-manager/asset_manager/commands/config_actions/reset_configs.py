from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction, CliOption


class ResetConfigs(CliAction):
    name = "reset"
    help_msg = "Remove custom configurations set by user and restore to factory defaults"
    requires_repo = False
    requires_store = False
    requires_auth = False

    def run(self, args):
        SettingsAPI().reset_user_configs(keys=[args.key] if args.key else [])

    def get_options(self):
        return [
            CliOption(
                dest="key",
                help_msg="config key to reset",
                short_name="k",
                full_name="key",
                n_args="?"
            )
        ]
