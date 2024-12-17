from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction


class StoreClear(CliAction):
    name = "clear"
    help_msg = "removes the asset-home and clears all its contents"
    requires_store = False
    requires_repo = False

    def run(self, args):
        SettingsAPI().remove_asset_home()

    def get_options(self):
        return []
