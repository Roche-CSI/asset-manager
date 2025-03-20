import os


class RemoteConfig:

    @property
    def contents_dir(self):
        return "contents"

    def contents_url(self, staging=False):
        return os.path.join("{storage_url}", self.contents_dir)

    @property
    def assets_dir(self):
        return "assets"

    @property
    def assets_url(self):
        return os.path.join("{storage_url}", self.assets_dir)

    @property
    def asset_classes_dir(self):
        return "asset_classes"

    @property
    def asset_classes_url(self):
        return os.path.join("{storage_url}", self.asset_classes_dir)

    @property
    def asset_aliases_dir(self):
        return "asset_aliases"

    @property
    def asset_aliases_url(self):
        return os.path.join("{storage_url}", self.asset_aliases_dir)
