import os
from asset_core.configs.app_settings import AppSettings
from asset_utils.utils.log_utils import colored_string, LogColors
from asset_manager.commands import CliAction, CliOption


class AuthSet(CliAction):
    name = "set"
    help_msg = "Set the path to auth file"
    requires_repo = False
    requires_store = False

    def run(self, args):
        if args.user:
            self.add_user(args)
        else:
            self.add_gcp_auth(args)

    def add_user(self, args):
        if not args.target:
            self.user_log.message("error", LogColors.ERROR)
            self.user_log.message("missing username", LogColors.ERROR)
            return
        # add to globals yaml
        settings = AppSettings.shared()
        settings.user = args.target
        msg = f"{colored_string('Success', color=LogColors.SUCCESS)}\n"
        msg += colored_string(f"asset-manager user set to: {settings.user}", LogColors.INFO)
        self.user_log.message(msg)

    def add_gcp_auth(self, args):
        if not args.target:
            self.user_log.message("error", LogColors.ERROR)
            self.user_log.message("missing credentials path", LogColors.ERROR)
            return

        # check if file exists
        target = os.path.abspath(args.target)
        if not os.path.exists(target) or not os.path.isfile(target):
            msg = "invalid argument, file doesn't exist"
            self.user_log.message(msg, LogColors.ERROR)
            return

        # add to globals yaml
        settings = AppSettings.shared()
        settings.auth = target
        msg = f"{colored_string('Success', color=LogColors.SUCCESS)}\n"
        msg += colored_string(f"asset-manager auth set to: {target}", LogColors.INFO)
        self.user_log.message(msg)

    def get_options(self):
        return [
            CliOption(
                dest="target",
                help_msg="path to gcp credentials file",
                positional=True
            ),
            # add user, this is temporary until we have asset credentials
            CliOption(
                dest="user",
                help_msg="add user to asset",
                is_boolean=True
            ),
        ]
