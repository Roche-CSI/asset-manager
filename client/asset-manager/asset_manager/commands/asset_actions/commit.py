import cached_property
from asset_core.api.repo_api import AssetAPI, AddAPI
from asset_manager.commands import CliAction, CliOption


class CommitMessage(CliAction):
    name = "commit"
    help_msg = "commit message for the changes"

    @cached_property.cached_property
    def api(self) -> AddAPI:
        return AssetAPI(self.repo).add

    def run(self, args):
        if args.message:
            self.api.add_commit_message(message=args.message)
        else:
            self.user_log.message("missing commit message, please use asset commit -m <message text>")

    def get_options(self):
        return [
            CliOption(dest="message",
                      help_msg="commit message",
                      short_name="m",
                      full_name="message"
                      )
        ]
