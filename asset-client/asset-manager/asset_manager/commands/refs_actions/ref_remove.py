from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class RemoveRef(CliAction):
    name = "remove"
    help_msg = "remove inputs from an asset"

    def run(self, args):
        api = AssetAPI(self.repo).remove
        with api.environment():
            api.remove_refs(targets=args.names)

    def get_options(self):
        return [
            CliOption(
                dest="names",
                help_msg="asset names to be removed from references",
                n_args="*",
                positional=True
            ),
            CliOption(
                dest="yes",
                help_msg="if true, asset-manager won't prompt user to confirm",
                is_boolean=True
            )
        ]
