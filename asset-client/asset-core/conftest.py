import logging
import os
import shutil
import tempfile
from unittest.mock import MagicMock

import pytest

from asset_core.asset import Asset
from asset_core.configs import Configs
from asset_core.configs.app_settings import AppSettings
from asset_core.objects.object_factory import ObjectFactory
from asset_core.plugins import list_files
from asset_core.store import Repo, AssetStore
from asset_manager.app import register_plugins
from asset_pluggy.storage import StorageData

logger = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """ pytest_sessionstart hook

    This runs *before* import and collection of tests.

    This is *THE* place to do mocking of things that are global,
    such as `appdirs`.

    Do tear down in `pytest_sessionfinish()`
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


@pytest.fixture(scope="session")
def test_environment(asset_root):
    data = {
        "auth": "/Users/google.json",
        "assets_home": os.environ.get("ASSET_HOME"),
        "user": {
            "id": "27e90950-8ebc-46bf-8743-c8b5a3a436eb",
            "username": "test_user",
            "email": "test_user@blah.com",
            "token": None
        },
        "projects": {
            "e803dcc6-9208-451e-88d9-7f99d7eecbd9": {
                "id": "e803dcc6-9208-451e-88d9-7f99d7eecbd9",
                "name": "asset-manager-test",
                "is_active": True,
                "staging_url": "gs://test_bucket/assets/staging",
                "remote_url": "gs://test_bucket/assets/remote",
                "can_edit": True,
                "can_read": True,
                "can_delete": False,
                "credentials_user": "test_user",
            }
        },
        "active_project": "e803dcc6-9208-451e-88d9-7f99d7eecbd9"
    }
    return data


@pytest.fixture(scope="session")
def store(asset_root, test_environment):
    yield __setup_store(environment=test_environment)
    logger.info("tearing down")
    shutil.rmtree(path=asset_root)


@pytest.fixture(scope="session")
def repo(store):
    """
    creates a temporary assets repo and makes it available
    cleans up the repo after work is done
    """
    temp_dir = os.path.realpath(tempfile.mkdtemp())
    yield __setup_repo(store=store, dir=temp_dir)

    logger.info("tearing down")
    shutil.rmtree(path=temp_dir)


@pytest.fixture(scope="session")
def test_data(repo):
    """
    copies test data into a temp project directory and
    makes available the added data files for testing
    """
    project_dir = os.path.abspath(os.path.dirname(__file__))
    test_data_dir = f"{project_dir}/test_data/file_types/jpegs"

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
    sources = ObjectFactory().parse_sources(repo_dir=repo.fs_path, targets=files)
    asset = Asset.create_new(repo=repo, class_id="3350b6d5-ded4-4ccf-adab-d5b6b8920041", class_name="group_test")
    asset.create_and_add_objects(sources)
    return asset


@pytest.fixture(scope="session")
def empty_asset(repo):
    return Asset.create_new(repo=repo, class_id="3350b6d5-ded4-4ccf-adab-d5b6b8920041", class_name="group_test")


def __setup_store(environment):
    # initialize store
    settings = AppSettings.shared()
    settings.data = AppSettings.validate(data=environment)
    settings.set_project_environment(project_id=settings.active_project)
    return AssetStore.create_store()


def __setup_repo(store, dir):
    # initialize assets
    repo = Repo.create_repo(root_dir=dir)
    logger.info("setting up, created assets repo at:{}".format(repo))
    # make sure it got created
    assert os.path.exists(os.path.join(str(repo), Repo.asset_dir()))
    return repo


@pytest.fixture(scope="session")
def mock_gcs_blob():
    blob = MagicMock(spec=StorageData)
    blob.content_type = "image/jpeg"
    blob.size = 12853831
    blob.name = "file_types/jpegs/photo-1522364723953-452d3431c267.jpg"
    blob.url = "gs://test_bucket/file_types/jpegs/photo-1522364723953-452d3431c267.jpg"
    blob.get_hash.return_value = ('md5', '4N7Mr93Wbtzm5j104ol0Mw==')
    return blob


@pytest.fixture(scope="session")
def mock_s3_blob():
    blob = MagicMock(spec=StorageData)
    blob.content_type = "application/octet-stream"
    blob.size = 17160
    blob.name = "file_types/csvs/customers.csv"
    blob.url = "s3://test_bucket/file_types/csvs/customers.csv"
    blob.get_hash.return_value = ('md5', 'eIlrw2PBTOr3VKXLHClkTQ==')
    return blob


@pytest.fixture(scope="session")
def mock_gcr_blob():
    blob = MagicMock(spec=StorageData)
    blob.name = 'my-test-project/my-test-image'
    blob.content_type = 'application/vnd.docker.distribution.manifest.v2+json'
    blob.size = 2391153464
    blob.host = 'gcr.io'
    blob.tag = ['latest']
    blob.path_in_asset = 'my-test-project/my-test-image'
    blob.url = 'gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890'
    blob.get_hash.return_value = ('sha256', '1234567890abcdef1234567890abcdef1234567890abcdef1234567890')
    return blob
