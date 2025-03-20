from asset_utils.common.user_commands import UserCommands
from asset_core.api.store_api import ContentHashAPI
from asset_manager.commands import CliAction, CliOption


class ComputeHashAction(CliAction):
    name = "hash"
    help_msg = "Calculate hash for target file or url"
    requires_repo = False
    requires_store = False

    def run(self, args):
        if not args.target:
            self.user_log.message("missing required parameter file")
            self.user_log.message(f"to clone an asset: {UserCommands().compute_hash()}")
            return
        ContentHashAPI().content_hash(src=args.target)

    def get_options(self):
        return [
            CliOption(dest="target",
                      help_msg="file or url",
                      positional=True
                      )
        ]
