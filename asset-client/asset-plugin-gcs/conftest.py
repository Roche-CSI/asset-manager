import logging
import os

import pytest

logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """ pytest_sessionstart hook

    This runs *before* import and collection of tests.

    This is *THE* place to do mocking of things that are global,
    such as `appdirs`.

    Do teardown in `pytest_sessionfinish()`
    """
    logger.info("Pre-Session Setup..")


def pytest_sessionfinish(session, exitstatus):
    """ pytest_sessionfinish hook

    This runs *after* any finalizers or other session activities.

    Performs teardown for `pytest_sessionstart()`
    """
    logger.info("\nPost-session Teardown..")


@pytest.fixture(scope="session")
def project_root():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="session")
def test_data():
    project_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(project_dir, "test_data")


@pytest.fixture(scope="session")
def mock_bucket(test_data):
    """Path to the mock bucket"""
    return os.path.join(test_data, "mock_bucket")
