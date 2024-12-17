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
def test_data(project_root):
    return os.path.join(project_root, "test_data")
