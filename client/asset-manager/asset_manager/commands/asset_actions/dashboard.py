from asset_core.api.settings_api import SettingsAPI
from asset_manager.commands import CliAction


class AssetDashboard(CliAction):
    name = "dashboard"
    help_msg = "opens the Asset Dashboard"

    requires_store = False
    requires_repo = False
    requires_auth = False

    def run(self, args):
        SettingsAPI().open_asset_dashboard()

    def get_options(self):
        return []
