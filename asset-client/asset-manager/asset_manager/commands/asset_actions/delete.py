from asset_manager.commands import CliAction, CliOption


class AssetDelete(CliAction):
    name = "delete"
    help_msg = "Deletes the asset"

    def run(self, args):
        # todo: connect with diff api
        # list_assets(repo=self.repo)
        # AssetAPI(self.repo).list.list()
        pass

    def get_options(self):
        return [
            CliOption(dest="asset_name",
                      help_msg="asset_name to delete from local",
                      n_args="?",
                      positional=True
                      ),
            CliOption(dest="upload",
                      help_msg="if yes, the asset is deleted from remote as well",
                      positional=True,
                      )
        ]
