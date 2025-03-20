from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands.cli_action import CliAction


class StoreInfo(CliAction):
    name = "info"
    help_msg = "List the path asset home"
    requires_repo = False
    requires_store = False

    def run(self, args):
        SettingsAPI().asset_home_info()

    def get_options(self):
        return []
