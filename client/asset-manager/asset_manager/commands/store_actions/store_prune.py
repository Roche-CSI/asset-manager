from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands.cli_action import CliAction


class StorePrune(CliAction):
    name = "prune"
    help_msg = "Remove invalid assets from the asset-store"
    requires_repo = False
    requires_store = False

    def run(self, args):
        SettingsAPI().prune_asset_store()

    def get_options(self):
        return []
