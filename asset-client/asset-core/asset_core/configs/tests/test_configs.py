import logging
import os

from asset_core.configs.configs import Configs
from asset_utils.utils import utils

logger = logging.getLogger(__file__)


def test_remote_configs():
    config = Configs.shared()
    assert config.remote.contents_url(staging=False) == "{storage_url}/contents"
    assert config.remote.contents_url(staging=True) == "{storage_url}/contents"
    assert config.remote.assets_url == '{storage_url}/assets'


def test_server_configs():
    config = Configs.shared()
    assert config.server.server_url == "http://localhost:5000"
    assert config.server.asset_route == "asset"
    assert config.server.asset_class_route == "asset_class"
    assert config.server.asset_commit_route == "asset_commit"


def test_settings_config():
    config = Configs.shared()
    assert config.settings.settings_file == os.path.join(
        utils.user_home_dir(),
        config.settings.settings_dir,
        "globals.json"
    )
    assert config.settings.default_home_dir == utils.user_home_dir()


def test_asset_config():
    configs = Configs.shared()
    assert configs.asset.asset_dir == ".asset"
