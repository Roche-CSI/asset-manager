from asset_core.api.store_api import ListAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors


class ListAssets(CliAction):
    name = "list"
    help_msg = "Lists the assets in the current asset-class"
    requires_repo = False

    def run(self, args):
        class_name = args.class_name or self.get_class_name()
        if not class_name:
            if not self.repo:
                msg = colored_string("you are not inside an asset directory\n", LogColors.ERROR)
            else:
                msg = colored_string("there are no active assets \n", LogColors.ERROR)
                msg += f"{UserCommands().create_asset()}\n"

            cmd = UserCommands()
            msg += "\n".join([cmd.list_assets(), cmd.list_classes(), cmd.list_help()])
            self.user_log.message(msg)
            return

        api = ListAPI(store=self.asset_store, repo=self.repo)
        with api.environment():
            api.list_assets(class_name=class_name, include_locations=args.locations)

    def get_class_name(self):
        if not self.repo or not self.repo.current_asset:
            return None
        return self.repo.current_asset.get("asset_class").get("name")

    def get_options(self):
        return [
            CliOption(
                dest="class_name",
                help_msg="the asset-class to list the assets for",
                short_name="c",
                full_name="class"
            ),
            CliOption(
                dest="locations",
                help_msg="list the assets available with their locations",
                is_boolean=True,
                short_name="l",
                full_name="locations",
            ),
        ]
