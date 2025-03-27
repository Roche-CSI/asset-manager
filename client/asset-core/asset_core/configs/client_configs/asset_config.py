class AssetConfig:
    """Configuration for asset related settings.

    Use @property instead of attributes to prevent them from being reassigned directly.
    """

    @property
    def asset_dir(self):
        return ".asset"

    @property
    def asset_file_name(self):
        return "asset.yaml"

    @property
    def repo_file(self):
        return "repo.json"

    @property
    def content_stats_file(self):
        return "file_stats.json"

    @property
    def states_dir(self):
        return "states"

    @property
    def manifests_dir(self):
        return "manifests"

    @property
    def default_cloud_store(self):
        return "gs"
