from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class RemoveFromAsset(CliAction):
    name = "remove"
    help_msg = "remove the following from asset: files, alias, refs"

    def run(self, args):
        api = AssetAPI(self.repo).remove
        with api.environment():
            api.remove_files(args.target, prompt_user=(not args.yes))
            # if args.ref:
            #     api.remove_refs(args.target)
            # elif args.alias:
            #     api.remove_alias(args.target)
            # else:
            #     api.remove_files(args.target, prompt_user=(not args.yes))

    def get_options(self):
        return [
            CliOption(
                dest="target",
                help_msg="files or directories to to remove from asset",
                n_args="*",
                positional=True
            ),
            # CliOption(
            #     dest="ref",
            #     help_msg="add reference to asset",
            #     is_boolean=True
            # ),
            # CliOption(dest="alias",
            #           help_msg="add alias to the asset",
            #           is_boolean=True
            #           ),
            CliOption(dest="yes",
                      help_msg="if true, asset-manager won't prompt user to confirm",
                      is_boolean=True
                      )
        ]
