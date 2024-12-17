from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class DebugAsset(CliAction):
    name = "debug"
    help_msg = "Debug asset data"
    requires_repo = True

    def run(self, args):
        api = AssetAPI(self.repo).debug
        with api.environment():
            api.run(name=args.name)

    def get_options(self):
        return [
            CliOption(dest="name",
                      help_msg="debug name",
                      positional=True)
        ]
