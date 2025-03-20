from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class UploadAsset(CliAction):
    name = "upload"
    help_msg = "upload asset to remote"

    def run(self, args):
        api = AssetAPI(self.repo).upload
        with api.environment():
            api.sync_to_remote(commit_msg=args.message)

    def get_options(self):
        return [
            CliOption(
                dest="message",
                help_msg="add commit message",
                short_name="m",
                full_name="message"
            )
        ]
