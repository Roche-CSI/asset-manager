import logging
import os

import pytest

from server_core.app import create_app
from server_core.asset_client.asset import Asset
from server_core.configs import Configs
from server_core.models import delete_tables, create_tables, User, Project, AssetClass
from server_core.plugins import register_plugins
from server_core.utils.file_utils import FileUtils

logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """ pytest_sessionstart hook

    This runs *before* import and collection of tests.

    This is *THE* place to do mocking of things that are global,
    such as `appdirs`.

    Do teardown in `pytest_sessionfinish()`
    """
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise Exception("missing required environemnt variable: GOOGLE_APPLICATION_CREDENTIALS")
    
    logger.info("Pre-Session Setup..")
    Configs.de_init()  # cleanup existing settings if any
    Configs.shared(mode=Configs.modes.TEST)  # all tests to use test_settings only
    register_plugins()


def pytest_sessionfinish(session, exitstatus):
    """ pytest_sessionfinish hook

    This runs *after* any finalizers or other session activities.

    Performs teardown for `pytest_sessionstart()`
    """
    logger.info("\nPost-session Teardown..")
    Configs.de_init()  # cleanup


@pytest.fixture(scope="session")
def client_asset():
    path = os.path.join(os.path.dirname(__file__), "server_core/asset_client/tests/test_data.json")
    asset = Asset(user="user1", data=FileUtils.read_json(path))
    return asset


@pytest.fixture(scope="session")
def test_server():
    app = create_app()
    delete_tables(app.db)  # delete
    create_tables(app.db)
    yield app


@pytest.fixture(scope="session")
def test_app(test_server):
    with test_server.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def test_user(test_app):
    # create and return user
    user: User = User.get_or_create(user="user1", username="test_user", email="dummy@dull.com")[0]
    yield user
    user.delete(user="user1", permanently=True)


@pytest.fixture(scope="session")
def test_project(test_user, test_app):
    # switch to a fixed id so we can manually inspect the project in the db
    project_id = "00000001-0001-0001-0001-000000000001"
    project: Project = Project.get_or_create(id=project_id,
                                             user=test_user.username,
                                             name="test_project",
                                             is_active=True,
                                             staging_url="random_url",
                                             remote_url="random_url")[0]

    project.credentials_server = FileUtils.read_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    gcs_url = "gs://placeholder_bukcet/server_test/{}"
    project.remote_url = gcs_url.format(project.id)
    project.save(user=test_user.username, only=[Project.remote_url, Project.credentials_server])
    yield project

    project.delete_instance(user="user1", permanently=True)


@pytest.fixture(scope="session")
def test_asset_class(test_user, test_project):
    # test_app fixture required for db transactions
    asset_cls = AssetClass.get_or_none(AssetClass.name == "gene_data", AssetClass.project == test_project)
    if not asset_cls:
        asset_cls = AssetClass.create(name="gene_data", project=test_project, user=test_user.username)
    yield asset_cls
    asset_cls.delete_instance(user=test_user, permanently=True)
    assert AssetClass.get_if_exists(AssetClass.id == asset_cls.id, include_deleted_records=True) is None