from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AliasInfo(CliAction):
    name = "info"
    help_msg = "view information on asset alias"

    def run(self, args):
        api = AssetAPI(self.repo).info
        with api.environment():
            api.list_alias()

    def get_options(self) -> [CliOption]:
        return []
