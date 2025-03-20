from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction, CliOption


class StoreClear(CliAction):
    name = "clear"
    help_msg = "Remove the asset-store and clears all its contents"
    requires_store = False
    requires_repo = False

    def run(self, args):
        SettingsAPI().remove_asset_home(confirm=args.yes)

    def get_options(self):
        return [
            CliOption(
                dest="yes",
                help_msg="don't prompt user to confirm",
                is_boolean=True,
                short_name="y",
                full_name="yes",
            ),
        ]
