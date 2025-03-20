from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AssetHistory(CliAction):
    name = "history"
    help_msg = "list versions history of the asset"

    def run(self, args):
        api = AssetAPI(self.repo).version
        with api.environment():
            api.list_version_history(large=args.large, list_all=args.all)

    def get_options(self):
        return [
            CliOption(
                dest="large",
                help_msg="optional: display detailed history of the asset",
                is_boolean=True
            ),
            CliOption(
                dest="all",
                help_msg="optional: display history of all the available versions",
                is_boolean=True
            ),
        ]
