from asset_utils.utils.web_utils import open_in_browser
from .repo import RepoAPI


class DebugAPI(RepoAPI):
    """debug helper"""

    # load_asset = False

    def run(self, name=None):
        """discards all local changes to an asset and restores it back to its previous
        committed version
        """
        if not name or name == "manifest":
            open_in_browser(self.asset.manifest_file)
        elif name == "state":
            open_in_browser(self.asset.states_file)
        elif name == "stats":
            open_in_browser(self.asset.object_stats_db.path)
        else:
            self.user_log.error(f"invalid option:{name}, select one of the following")
            self.user_log.message(["manifest", "state"], bulleted=True)
