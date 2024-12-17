from asset_manager.commands import CliAction
from asset_core.api.repo_api import AssetAPI


class ListAssetVersion(CliAction):
    name = "versions"
    help_msg = "Lists version information of the asset"

    def run(self, args):
        api = AssetAPI(repo=self.repo).version
        with api.environment():
            api.list_versions_summary()

    def get_options(self):
        return []
