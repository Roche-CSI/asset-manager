from asset_manager.commands import CliAction, CliOption


class UploadAssetClass(CliAction):
    name = "upload"
    help_msg = "Upload an asset-class that's not yet updated to server"
    requires_repo = False

    def run(self, args):
        # todo: create asset-class with server
        # fetch asset-class list from bucket
        print(f"to be implemented: discard asset-class:{args.class_name}")
        pass

    def get_options(self):
        return [
            CliOption(dest="class_name",
                      help_msg="enter a name for the asset-class you want to create",
                      positional=True
                      ),
        ]
