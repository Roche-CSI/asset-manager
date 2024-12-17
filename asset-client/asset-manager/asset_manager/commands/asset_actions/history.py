from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AssetHistory(CliAction):
    name = "history"
    help_msg = "display version history of the asset"

    def run(self, args):
        api = AssetAPI(self.repo).version
        with api.environment():
            api.list_version_history(large=args.large)

    def get_options(self):
        return [
            CliOption(
                dest="large",
                help_msg="displays large table, if true",
                is_boolean=True
            )
        ]
