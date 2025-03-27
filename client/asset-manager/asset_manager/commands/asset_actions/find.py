from asset_core.api.store_api import FindAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.utils.log_utils import LogColors


class AssetFind(CliAction):
    name = "find"
    help_msg = "finds the name or size of an asset"
    requires_repo = False

    def run(self, args):
        if args.alias and not args.class_name:
            self.user_log.message("missing required param: class_name", LogColors.ALERT)
            return
        api = FindAPI(store=self.asset_store, repo=self.repo)
        with api.environment():
            if args.size:
                api.find_asset_size(asset_version_name=args.size)
                return
            # find asset name for the given alias or hash
            asset_name = api.find_asset(class_name=args.class_name, hash=args.hash, alias=args.alias)
            self.user_log.message(asset_name, formatted=False)

    def get_options(self):
        return [
            CliOption(
                dest="class_name",
                help_msg="class name of the asset you want to find",
                short_name="c",
                full_name="class"
            ),
            CliOption(
                dest="alias",
                help_msg="alias of the asset seq id. returns the <class_name>/<seq_id> of the asset",
                short_name="a",
                full_name="alias"
            ),
            CliOption(
                dest="hash",
                help_msg="hash of the asset version. returns the <class_name>/<seq_id>/<version> of the asset",
                short_name="ha",
                full_name="hash"
            ),
            CliOption(
                dest="size",
                help_msg="asset version name of the asset you want to find the size of",
                short_name="s",
                full_name="size"
            )
        ]
