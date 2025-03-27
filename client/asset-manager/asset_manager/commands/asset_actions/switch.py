from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors


class AssetSwitch(CliAction):
    name = "switch"
    help_msg = "switch to a different version"

    def run(self, args):
        if not args.version:
            msg = colored_string("did you forget to pass the version number?\n", LogColors.INFO)
            msg += UserCommands().switch_asset_version()
            self.user_log.message(msg)
            return

        api = AssetAPI(repo=self.repo).switch
        with api.environment():
            api.switch_to_version(ver_number=args.version, ask_confirmation=(not args.yes))

    def get_options(self):
        return [
            CliOption(
                dest="version",
                help_msg="version number you want to switch to",
                short_name="v",
                full_name="version",
            ),
            CliOption(
                dest="yes",
                help_msg="if true, asset-manager won't prompt user to confirm",
                is_boolean=True,
                short_name="y",
                full_name="yes",
            ),
        ]
