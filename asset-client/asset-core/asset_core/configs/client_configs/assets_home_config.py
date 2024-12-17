import os

from asset_core.configs.config_modes import ConfigModes

DEV_DASHBOARD = "http://localhost:3000"
PROD_DASHBOARD = "PROD_DASHBOARD_URL"
USER_TEST_DASHBOARD = "SANDBOX_DASHBOARD_URL"


class AssetsHomeConfig:

    def __init__(self, mode: ConfigModes):
        self._mode = mode

    @property
    def asset_store_dir(self):
        return os.path.join("{asset_home}", ".assets")

    @property
    def asset_store_backup_dir(self):
        return os.path.join("{asset_home}", ".assets_backup")

    @property
    def asset_store_file(self):
        return "store.json"

    @property
    def assets_dir(self):
        return os.path.join(self.asset_store_dir, "{project_id}")

    @property
    def cache_dir(self):
        return self.assets_dir

    @property
    def assets_cache_dir(self):
        return os.path.join(self.cache_dir, "assets")

    @property
    def contents_cache_dir(self):
        return os.path.join(self.cache_dir, "contents", "{class_id}")

    @property
    def asset_classes_cache_dir(self):
        return os.path.join(self.cache_dir, "asset_classes")

    @property
    def asset_class_file(self):
        return os.path.join(self.asset_classes_cache_dir, "{class_id}.yaml")

    @property
    def manifests_cache_dir(self):
        return os.path.join(self.cache_dir, "manifests")

    @property
    def content_stats_file(self):
        return os.path.join(self.cache_dir, "content_stats", "{class_id}.json")

    @property
    def class_list_file_name(self):
        return "class_list.yaml"

    @property
    def class_list_file(self):
        return os.path.join(self.asset_classes_cache_dir, self.class_list_file_name)

    @property
    def hash_list_file(self):
        return os.path.join(self.cache_dir, "meta_hashes.json")

    @property
    def asset_list_file_name(self):
        return "asset_list.yaml"

    @property
    def dashboard_url(self):
        if self._mode == ConfigModes.PRODUCTION:
            return PROD_DASHBOARD
        if self._mode == ConfigModes.USER_TEST:
            return USER_TEST_DASHBOARD

        return DEV_DASHBOARD
