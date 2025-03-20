import os

from asset_utils.utils import utils


class SettingsConfig:

    @property
    def settings_dir(self):
        """ASSET_ROOT
         - is where the asset-manager settings are stored i.e  .asset-manager/globals.json
        """
        return os.path.join(os.getenv("ASSET_ROOT") or self.default_home_dir, ".asset-manager")

    @property
    def settings_file(self):
        return os.path.join(self.settings_dir, "globals.json")

    @property
    def default_home_dir(self):
        return utils.user_home_dir()
