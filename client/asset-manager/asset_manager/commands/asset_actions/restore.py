from asset_manager.commands import CliAction, CliOption


class AssetRestore(CliAction):
    name = "restore"
    help_msg = "Restores a deleted asset"

    def run(self, args):
        # todo: connect with diff api
        # list_assets(repo=self.repo)
        # AssetAPI(self.repo).list.list()
        pass

    def get_options(self):
        return [
            CliOption(dest="asset_name",
                      help_msg="asset_name to restore",
                      n_args="1",
                      positional=True
                      )
        ]
