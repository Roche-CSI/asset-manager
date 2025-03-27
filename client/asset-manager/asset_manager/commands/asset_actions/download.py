import os
from asset_manager.commands import CliAction, CliOption
from asset_core.api.repo_api import AssetAPI


class DownloadAsset(CliAction):
    name = "download"
    help_msg = "download the asset"

    def run(self, args):
        api = AssetAPI(repo=self.repo).download
        if args.credentials:
            os.environ["ASSET_CREDENTIALS"] = args.credentials
        with api.environment():
            api.download_asset(files=args.files)
            # unset credentials
            if args.credentials:
                os.unsetenv("ASSET_CREDENTIALS")

    def get_options(self):
        return [
            CliOption(dest="files",
                      help_msg="files to download, if missing - all files will be downloaded",
                      n_args="*",
                      positional=True),

            CliOption(dest="credentials",
                      full_name="cred",
                      short_name="c",
                      help_msg="optional credentials to use for download",
                      n_args="?")
        ]
