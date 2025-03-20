import json
import os

from asset_core.configs import AppSettings


def test_settings_environment(test_environment):
    """make sure test_environment has all the required data"""
    assert AppSettings.validate(data=test_environment)


def test_settings_location(asset_root):
    """for testing we create an isolated environment to prevent collision and data corruption
    with installed asset-manager or the asset-manager dev environment
    """
    assert os.getenv("ASSET_ROOT") == asset_root
    assert os.getenv("ASSET_HOME") == asset_root


def test_settings_yaml(store, test_environment):
    stg = AppSettings.shared()
    assert json.dumps(stg.data) == json.dumps(test_environment)
