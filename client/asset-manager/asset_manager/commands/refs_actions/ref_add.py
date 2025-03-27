from asset_core.api.repo_api import AssetAPI, AddAPI
from asset_core.configs import AppSettings
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands


class AddRef(CliAction):
    name = "add"
    help_msg = "add inputs to an asset"
    requires_repo = False
    requires_store = True

    # TODO: refactor all the refs functions into a RefsAPI
    def run(self, args):
        if args.remote_asset:
            # remote refs can be added from inside or outside asset repo
            with AppSettings.shared().project_environment(project_id=AppSettings.shared().active_project):
                AddAPI.add_ref_to_remote_asset(src_name=args.input_asset,
                                               label=args.label,
                                               dst_name=args.remote_asset,
                                               properties=args.properties)
        elif self.repo:
            # local refs can be added only from inside asset repo
            api = AssetAPI(self.repo).add
            with api.environment():
                api.add_ref(src_name=args.input_asset,
                            label=args.label,
                            properties=args.properties)
        else:
            # not remote ref and not inside asset repo
            self.user_log.info("you need to be inside an asset directory or use remote asset to add refs")
            self.user_log.message(UserCommands().inputs_add())
            self.user_log.message(UserCommands().inputs_add_remote())

    def get_options(self) -> [CliOption]:
        return [
            CliOption(
                dest="input_asset",
                help_msg="asset name to add as inputs",
                n_args="?",
                positional=True,
            ),
            CliOption(
                dest="label",
                short_name="l",
                full_name="label",
                help_msg="label of the input",
                n_args="?",
            ),
            CliOption(
                dest="properties",
                short_name="p",
                full_name="properties",
                help_msg="properties of the input",
                n_args="?",
            ),
            CliOption(
                dest="remote_asset",
                short_name="r",
                full_name="remote",
                help_msg="asset name to add the input to. remote inputs will be directly added to the database",
                n_args="?",
            ),
        ]
