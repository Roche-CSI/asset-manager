import logging
import os
import tempfile

import pytest

from asset_core.configs import Configs
from asset_core.configs.app_settings import AppSettings
from asset_manager.app import register_plugins

logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """ pytest_sessionstart hook

    This runs *before* import and collection of tests.

    Do teardown in `pytest_sessionfinish()`
    """
    logger.info("Pre-Session Setup..")
    Configs.de_init()  # cleanup existing settings if any
    Configs.shared(mode=Configs.modes.UNIT_TEST)  # all tests to use test_settings only
    register_plugins()


def pytest_sessionfinish(session, exitstatus):
    """ pytest_sessionfinish hook

    This runs *after* any finalizers or other session activities.

    Performs teardown for `pytest_sessionstart()`
    """
    logger.info("\nPost-session Teardown..")
    Configs.de_init()  # cleanup
    AppSettings.shared().unset_project_environment()


@pytest.fixture(scope="session")
def project_root():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="session")
def asset_root():
    os.environ["ASSET_ROOT"] = os.path.realpath(tempfile.mkdtemp())  # .asset-manager
    os.environ["ASSET_HOME"] = os.environ.get("ASSET_ROOT")  # .assets
    return os.environ.get("ASSET_ROOT")
