import os

from asset_core.api.repo_api import AssetAPI
from asset_manager.commands import CliAction, CliOption


class AddToAsset(CliAction):
    name = "add"
    help_msg = "add files to an asset"

    def run(self, args):
        api = AssetAPI(self.repo).add
        self.user_log.message(f"target: {args.target}")

        if args.credentials:
            os.environ["ASSET_CREDENTIALS"] = args.credentials
        with api.environment():
            api.add_files(targets=args.target,
                          prompt_user=(not args.yes),
                          object_type=args.type,
                          proxy=args.proxy,
                          dest_dir=args.dest_dir if args.dest_dir else None,
                          force=args.force)
            if args.credentials:
                os.unsetenv("ASSET_CREDENTIALS")

    def get_options(self) -> [CliOption]:
        return [
            CliOption(
                dest="target",
                help_msg="files or directories to add to asset, accepts wildcards i.e. *.txt etc",
                n_args="*",
                positional=True
            ),
            CliOption(
                dest="dest_dir",
                short_name="d",
                full_name="dir",
                n_args="?",
                help_msg="create a new directory and add files into it",
            ),
            CliOption(
                dest="type",
                short_name="t",
                full_name="type",
                n_args="?",
                help_msg="combine all files into a single group object (makes it efficient for large number of files)",
            ),
            CliOption(
                dest="proxy",
                help_msg="add as a proxy content",
                is_boolean=True
            ),
            CliOption(
                dest="yes",
                help_msg="if true, asset-manager won't prompt user to confirm",
                is_boolean=True
            ),
            CliOption(
                dest="credentials",
                help_msg="optional: gcs credentials to use for adding (for proxy assets), available only for gcs",
                short_name="c",
                full_name="cred"
            ),
            CliOption(
                dest="force",
                help_msg="force add files even if they are ignored by assetignore",
                is_boolean=True,
                short_name="f",
                full_name="force"
            ),
        ]
