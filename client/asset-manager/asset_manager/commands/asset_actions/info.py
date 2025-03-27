from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.common import exceptions
from asset_utils.utils.log_utils import LogColors


class AssetInfo(CliAction):
    name = "info"
    help_msg = "displays information of the asset"
    requires_repo = True

    def run(self, args):
        api = AssetAPI(repo=self.repo).info
        if not api:
            return
        try:
            with api.environment():
                if args.inputs:
                    api.list_refs()
                elif args.alias:
                    api.list_alias()
                elif args.name:
                    api.print_name()
                elif args.alias_name:
                    api.print_alias_name()
                elif args.url:
                    api.print_object_url(args.url)
                elif args.hash:
                    api.print_hash()
                elif args.metadata:
                    api.print_metadata()
                elif args.attributes:
                    api.print_attributes()
                else:
                    api.asset_info(args.large)
        except exceptions.AssetException as e:
            self.user_log.message(e.msg, color=LogColors.ERROR)

    def get_options(self):
        return [
            CliOption(
                dest="large",
                help_msg="show expanded information on the asset",
                is_boolean=True
            ),
            CliOption(
                dest="inputs",
                help_msg="list local inputs of the asset",
                is_boolean=True
            ),
            CliOption(
                dest="alias",
                help_msg="print the alias of the asset",
                is_boolean=True
            ),
            CliOption(
                dest="name",
                help_msg="print asset name",
                is_boolean=True
            ),
            CliOption(
                dest="alias_name",
                help_msg="print asset alias name",
                is_boolean=True
            ),
            CliOption(
                dest="url",
                help_msg="print the URL of a file in the asset",
                is_boolean=False,
                short_name="q",
                full_name="url",
                n_args="?",
            ),
            CliOption(
                dest="hash",
                help_msg="print asset commit hash",
                is_boolean=True
            ),
            CliOption(
                dest="metadata",
                help_msg="print asset metadata",
                is_boolean=True
            ),
            CliOption(
                dest="attributes",
                help_msg="print asset attributes",
                is_boolean=True
            ),
        ]
