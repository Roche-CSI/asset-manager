from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands


class InitAsset(CliAction):
    name = "init"
    help_msg = "Initialize Asset or Repo"
    requires_repo = False

    def get_options(self):
        return [
            CliOption(
                dest="class_name",
                help_msg="class-name in which to create an asset",
                positional=True
            ),
        ]

    def run(self, args):
        if not args.class_name:
            self.user_log.error("missing required parameter class-name")
            self.user_log.message(UserCommands().init_repo())
            return
        api = AssetAPI(repo=None).init
        with api.environment():
            api.create_asset(class_name=args.class_name)
