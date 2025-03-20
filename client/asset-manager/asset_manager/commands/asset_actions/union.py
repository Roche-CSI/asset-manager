from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AssetUnion(CliAction):
    name = "union"
    help_msg = "combine another version with current version of the asset"
    requires_repo = True

    def run(self, args):
        api = AssetAPI(repo=self.repo).union
        with api.environment():
            api.union(target_version=args.dst_version, file=args.file, continue_file=args.continue_file)

    def get_options(self):
        return [
            CliOption(dest="dst_version",
                      help_msg="target version for merge",
                      n_args="?",
                      positional=True),
            CliOption(dest="file",
                      short_name="f",
                      full_name="file",
                      help_msg="if specified, then only the give file from the specified version will be merged",
                      n_args="?"),
            CliOption(dest="continue_file",
                      short_name="c",
                      full_name="continue",
                      help_msg="file path",
                      n_args="?"),
        ]
