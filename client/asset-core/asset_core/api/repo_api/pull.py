from .repo import RepoAPI
from packaging.version import parse as parse_version
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher


class AssetPullAPI(RepoAPI):

    def pull_asset(self):
        if self.asset.is_temp:
            self.user_log.message("asset not committed yet, so no versions available")
            return

        # download meta information
        fetcher = AssetFetcher(store=self.asset.repo.store)
        self.user_log.message(f"checking for updates to asset:{self.asset.name}")
        if not fetcher.download_dir(dir_url=self.asset.remote_url,
                                    dir_dst=self.asset.cache_dir):
            self.user_log.message("there are no updates to this asset")
            return

        # check the latest updates and inform user
        versions = self.asset.cached_versions()
        current_ver = parse_version(self.asset.version.number)
        updates = []
        for version in versions:
            if current_ver < parse_version(version["number"]):
                updates.append(version)

        if updates:
            self.user_log.message(f"{len(updates)} new versions added to asset")
            self.versions_summary_table(versions=updates)

    def versions_summary_table(self, versions: [dict]):
        columns = {
            "version": "Version",
            "commit_hash": "Commit",
        }
        data = [{'version': version.get('number'),
                 'commit_hash': version.get('commit_hash')}
                for version in versions]
        self.user_log.table(columns=columns, rows=data, table_fmt="simple")
