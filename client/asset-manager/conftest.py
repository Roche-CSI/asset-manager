import logging
import os
import shutil
import tempfile

import pytest

from asset_core.asset import Asset
from asset_core.configs import Configs
from asset_core.configs.app_settings import AppSettings
from asset_core.objects.object_factory import ObjectFactory
from asset_core.plugins import list_files
from asset_core.store import Repo, AssetStore
from asset_manager.plugins import register_plugins

logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """ pytest_sessionstart hook

    This runs *before* import and collection of tests.

    This is *THE* place to do mocking of things that are global,
    such as `appdirs`.

    Do teardown in `pytest_sessionfinish()`
    """
    logger.info("Pre-Session Setup..")
    Configs.de_init()  # cleanup existing settings if any
    Configs.shared(mode=Configs.modes.UNIT_TEST)  # all tests to use test_settings only
    register_plugins()
    logger.info("Pre-Session Setup..")


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
    return os.path.abspath(tempfile.mkdtemp())


@pytest.fixture(scope="session")
def upload_test_url():
    return "gs://my-bucket/test/client/upload_tests/{date_string}"


@pytest.fixture(scope="session")
def copy_test_url():
    return "gs://my-bucket/test/client/copy_tests/{date_string}"


@pytest.fixture(scope="session")
def testing_home():
    return os.path.abspath(tempfile.mkdtemp())


@pytest.fixture(scope="session")
def asset_root(testing_home):
    root = os.path.realpath(testing_home)
    os.environ["ASSET_ROOT"] = os.path.join(root, "asset_root")  # parent of .asset-manager
    os.environ["ASSET_HOME"] = os.path.join(root, "asset_store")  # parent of .assets

    # set up app settings
    # set a separate settings for testing
    settings = AppSettings.shared()
    settings.data = test_globals_json(asset_home=root)

    return os.getenv("ASSET_HOME")


@pytest.fixture(scope="session")
def store(asset_root):
    settings = AppSettings.shared()
    # settings.data = AppSettings.validate(data=environment)
    settings.set_project_environment(project_id=settings.active_project)
    # settings.auth = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    store = AssetStore.create_store()
    yield store
    logger.info("tearing down")
    # shutil.rmtree(path=asset_root)


@pytest.fixture(scope="session")
def repo(asset_root, store):
    """
    creates a temporary assets repo and makes it available
    cleans up the repo after work is done
    """
    # temp_dir = os.path.realpath(tempfile.mkdtemp())
    yield __setup_repo(store=store, dir=asset_root)

    logger.info("tearing down")
    if os.path.exists(asset_root):
        shutil.rmtree(path=asset_root)


@pytest.fixture(scope="session")
def test_data(repo):
    """
    copies test data into a temp project directory and
    makes available the added data files for testing
    """
    project_dir = os.path.abspath(os.path.dirname(__file__))
    test_data_dir = f"{project_dir}/test_data"

    # copy files to repo
    target = os.path.join(repo.fs_path, test_data_dir)
    # make dir if not exists
    os.makedirs(target, exist_ok=True)
    target = os.path.join(repo.fs_path, "test_data")
    shutil.copytree(test_data_dir, target)

    return target


@pytest.fixture(scope="session")
def asset(repo, test_data):
    files = list_files(root_dir=test_data)
    sources: dict = ObjectFactory().parse_sources(repo_dir=repo.fs_path,
                                                  targets=files)
    asset = Asset.create_new(repo=repo, class_id="123e4567-e89b-12d3-a456-426614174000", class_name="myclass")
    asset.create_and_add_objects(sources)
    return asset


@pytest.fixture(scope="session")
def empty_asset(repo):
    asset = Asset.create_new(repo=repo, class_id="123e4567-e89b-12d3-a456-426614174000", class_name="myclass")


def __setup_repo(store, dir):
    # initialize assets
    repo = Repo.create_repo(root_dir=dir)
    repo.store = store
    logger.info("setting up, created assets repo at:{}".format(repo))
    # make sure it got created
    assert os.path.exists(os.path.join(str(repo), Repo.asset_dir()))
    return repo


def test_globals_json(asset_home):
    raise NotImplementedError("add a test globals.json dictionary here")
    return {
        """return test globals.json"""
    }
