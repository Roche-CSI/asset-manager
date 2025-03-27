from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AssetPull(CliAction):
    name = "pull"
    help_msg = "pull and switch to the latest version"

    def run(self, args):
        api = AssetAPI(repo=self.repo).switch
        with api.environment():
            api.switch_to_latest(force=args.force)

    def get_options(self):
        return [
            CliOption(
                dest="force",
                is_boolean=True,
                help_msg="version number you want to switch to",
                short_name="f",
                full_name="force",
            ),
        ]
