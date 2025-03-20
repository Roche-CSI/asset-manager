from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AssetDiscard(CliAction):
    name = "discard"
    help_msg = "discards a local asset"

    def run(self, args):
        api = AssetAPI(repo=self.repo).discard
        with api.environment():
            if args.all:
                api.discard_all_changes()
            elif args.staged:
                api.discard_staged_files(args.file)
            elif args.unstaged:
                api.discard_unstaged_files(args.file)
            else:
                self.user_log.message("invalid command")

    def get_options(self) -> [CliOption]:
        return [
            CliOption(
                dest="all",
                help_msg="remove all changes to asset",
                is_boolean=True
            ),
            CliOption(
                dest="staged",
                help_msg="remove staged changes",
                is_boolean=True
            ),
            CliOption(
                dest="unstaged",
                help_msg="remove unstaged changes",
                is_boolean=True
            ),
            CliOption(
                dest="file",
                short_name="f",
                full_name="file",
                help_msg="files in which changes will be discarded",
                n_args="*",
                positional=True
            )
        ]
