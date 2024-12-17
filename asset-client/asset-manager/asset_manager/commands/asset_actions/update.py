from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class UpdateAsset(CliAction):
    name = "update"
    help_msg = "update the asset with any changes to added files"

    def run(self, args):
        api = AssetAPI(self.repo).update
        with api.environment():
            if args.all:
                api.update_asset(prompt_user=(not args.yes))
            else:
                api.update_objects(args.target, prompt_user=(not args.yes))

    def get_options(self) -> [CliOption]:
        return [
            CliOption(
                dest="all",
                help_msg="update all the modified files",
                is_boolean=True
            ),
            CliOption(
                dest="target",
                help_msg="files to update",
                n_args="*",
                positional=True
            ),
            CliOption(
                dest="yes",
                help_msg="if true, asset-manager won't prompt user to confirm",
                is_boolean=True
            )
        ]
