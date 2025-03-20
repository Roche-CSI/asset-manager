import logging
import os

import pytest

logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """ pytest_sessionstart hook

    This runs *before* import and collection of tests.

    This is *THE* place to do mocking of things that are global,
    such as `appdirs`.

    Do tear down in `pytest_sessionfinish()`
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
def upload_test_url():
    return "s3://aws-test-bucket/test_data/upload_test/{date_string}"


@pytest.fixture(scope="session")
def copy_test_url():
    return "s3://aws-test-bucket/test_data/copy_tests/{date_string}"


@pytest.fixture(scope="session")
def aws_test_credentials():
    return {
        'aws_access_key_id': 'mock_access_key',
        'aws_secret_access_key': 'mock_secret_key',
        'region_name': 'us-east-1'
    }
