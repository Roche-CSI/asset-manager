from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.utils.log_utils import LogColors


class AddAlias(CliAction):
    name = "add"
    help_msg = "add alias to asset"

    def run(self, args):
        self.user_log.alert("'asset alias add' is getting deprecated. Please use 'asset alias set' instead.")
        api = AssetAPI(self.repo).add
        if not args.target:
            self.user_log.message("missing required parameter <alias>", color=LogColors.ERROR)
            return
        with api.environment():
            api.add_alias(args.target)

    def get_options(self) -> [CliOption]:
        return [
            CliOption(
                dest="target",
                help_msg="alias name",
                n_args="?",
                positional=True
            )
        ]
