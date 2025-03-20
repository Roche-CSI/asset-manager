from asset_manager.commands import CliAction, CliOption
from asset_core.api.repo_api import AssetAPI


class AssetDiff(CliAction):
    name = "diff"
    help_msg = "Displays the differences between two versions of an asset"

    def run(self, args):
        print(f"args: {args.__dict__}")
        api = AssetAPI(self.repo).diff
        with api.environment():
            api.diff(file=args.file, src_ver=args.src_ver, dst_ver=args.dst_ver, html=args.html)

    def get_options(self):
        return [
            CliOption(dest="src_ver",
                      short_name="s",
                      full_name="src",
                      help_msg="src version",
                      n_args="?",
                      ),
            CliOption(dest="dst_ver",
                      short_name="d",
                      full_name="dst",
                      help_msg="dst version",
                      n_args="?",
                      ),
            CliOption(dest="file",
                      short_name="f",
                      full_name="file",
                      help_msg="file path",
                      n_args="?",
                      ),
            CliOption(dest="html",
                      help_msg="if true diff is shown as html",
                      is_boolean=True
                      )
        ]
