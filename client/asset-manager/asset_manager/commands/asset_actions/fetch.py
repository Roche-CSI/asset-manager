from asset_core.api.store_api import FetchAPI
from asset_core.asset import Asset
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors


class FetchAsset(CliAction):
    name = "fetch"
    help_msg = "fetch asset and class metadata"
    requires_repo = False

    def run(self, args):
        api = FetchAPI(store=self.asset_store, repo=self.repo)
        with api.environment():
            if args.asset_name:
                api.fetch_asset(asset_name=args.asset_name, force=args.force)
            elif args.class_name:
                api.fetch_assets(class_name=args.class_name, force=args.force)
            elif args.all:
                api.fetch_all(force=args.force)
            elif not self.repo:
                self.user_log.message(self.repo_error())
            elif self.repo.current_asset:
                if args.versions:
                    api.fetch_versions(self.repo.current_asset)
                else:
                    api.fetch_asset(asset_name=Asset.get_name(self.repo.current_asset))
            else:
                # show help message to user
                message = colored_string("invalid, missing required parameter\n", LogColors.ERROR)
                cmd = UserCommands()
                message += "\n".join([cmd.fetch_assets(), cmd.fetch_classes(), cmd.fetch_help()])
                self.user_log.message(message)

    def repo_error(self):
        """subclass can override to return custom message"""
        message = colored_string("you are not inside an asset directory\n", color=LogColors.ERROR)
        cmd = UserCommands()
        message += "\n".join([cmd.fetch_assets(), cmd.fetch_classes(), cmd.fetch_help()])
        return message

    def get_options(self):
        return [
            CliOption(
                dest="asset_name",
                help_msg="fetch all the metadata of an asset",
                positional=True
            ),
            CliOption(
                dest="all",
                help_msg="fetch all classes and assets",
                is_boolean=True
            ),
            CliOption(
                dest="class_name",
                help_msg="fetch all assets for a class",
                short_name="c",
                full_name="class"
            ),
            CliOption(
                dest="force",
                help_msg="force download files even if exists",
                is_boolean=True
            ),
            CliOption(
                dest="versions",
                help_msg="fetch versions for an asset",
                is_boolean=True
            ),
        ]
