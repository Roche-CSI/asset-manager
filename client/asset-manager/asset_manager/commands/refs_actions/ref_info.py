from asset_core.api.repo_api import AssetAPI, InfoAPI
from asset_core.configs import AppSettings
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors


class RefsInfo(CliAction):
    name = "info"
    help_msg = "displays inputs information of the asset"
    requires_repo = False

    def run(self, args):
        if args.asset_name:
            asset_version_name = f"{args.asset_name}/{args.asset_version}" if args.asset_version else args.asset_name
            with AppSettings.shared().project_environment(project_id=AppSettings.shared().active_project):
                InfoAPI.list_remote_refs(asset_name=asset_version_name,
                                         project_id=AppSettings.shared().active_project)
        elif self.repo:
            api = AssetAPI(repo=self.repo).info
            with api.environment():
                api.list_refs(version=args.asset_version, remote=args.remote)
        else:
            self.user_log.alert("not inside an asset repo. asset name is required")
            self.user_log.message(UserCommands().inputs_info())
            self.user_log.message(UserCommands().inputs_info_remote())
            self.user_log.message(UserCommands().inputs_info_version())

    def get_options(self):
        return [
            CliOption(
                dest="asset_name",
                short_name="n",
                full_name="name",
                help_msg="asset name for which you want see the refs. Only remote refs will be displayed.",
                n_args="?"
            ),
            CliOption(
                dest="asset_version",
                short_name="v",
                full_name="version",
                help_msg="asset version for which you want see the refs. Only works on remote refs."
            ),
            CliOption(
                dest="remote",
                short_name="r",
                full_name="remote",
                help_msg="list remote refs.",
                is_boolean=True
            )
        ]

    def repo_error(self):
        """custom message when user is passing command from outside asset repo
        """
        message = colored_string("you are not inside an asset directory\n", color=LogColors.ERROR)
        message += f"{UserCommands().inputs_info()}\n"
        return message
