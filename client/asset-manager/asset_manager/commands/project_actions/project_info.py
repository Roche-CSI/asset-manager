from asset_manager.commands.cli_action import CliAction
from asset_core.api.settings_api import SettingsAPI


class ProjectInfo(CliAction):
    name = "info"
    help_msg = "prints project information"
    requires_repo = False
    requires_store = False

    def run(self, args):
        SettingsAPI().print_active_project()

    def get_options(self):
        return []
