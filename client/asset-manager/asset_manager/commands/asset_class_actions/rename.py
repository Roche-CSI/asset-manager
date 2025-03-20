from asset_manager.commands import CliAction, CliOption


class RenameAssetClass(CliAction):
    name = "rename"
    help_msg = "Rename an existing asset-class"
    requires_repo = False

    def run(self, args):
        # todo: create asset-class with server
        # fetch asset-class list from bucket
        print(f"to be implemented: rename asset-class: {args.class_name}, {args.new_name}")
        pass

    def get_options(self):
        return [
            CliOption(dest="class_name",
                      help_msg="enter a name for the asset-class you want to create",
                      positional=True
                      ),
            CliOption(dest="new_name",
                      help_msg="enter a name for the asset-class you want to create",
                      positional=True
                      ),
        ]
