import json
from unittest.mock import patch

import pytest

from asset_pluggy.plugin.storage_manager import StorageManager
from asset_pluggy.storage.asset_storage import AssetStorage
from asset_pluggy.storage.mount_config import MountConfig
from asset_pluggy.storage.storage_factory import StorageFactory
from asset_utils.common import exceptions


def test_storage_with_prefix():
    # this should succeed if installed
    prefixes = ["file://", "s3://", "gs://", "gcr.io/", "us.gcr.io/"]
    for prefix in prefixes:
        with pytest.raises(exceptions.InvalidStorageBackendError) as e:
            storage = StorageFactory.storage_with_prefix(prefix)
            assert issubclass(storage.__class__, AssetStorage)
            assert prefix in storage.prefixes
        assert str(e.value.args[0]) == f"{prefix} backend is not installed"

    # these should throw error
    prefixes = ["file", "s3", "gs", "gcr.io", "us.gcr.io"]
    for prefix in prefixes:
        with pytest.raises(exceptions.InvalidStorageBackendError) as e:
            _ = StorageFactory.storage_with_prefix(prefix)
        assert str(e.value.args[0]) == f"{prefix} backend is not installed"


def test_storage_for_url():
    # these should work once all plugins are installed
    urls = [
        ("gs://bucket/test/files/sample.yml", "gs://"),
        ("s3://bucket/test/test_data/sample.yml", "s3://"),
        ("gcr.io/project/image:my_tag", "gcr.io/"),
        ("folder/subfolder/sample.yml", "file://")
    ]
    for url, prefix in urls:
        with pytest.raises(exceptions.InvalidStorageBackendError) as e:
            storage = StorageFactory.storage_for_url(src_url=url)
            assert prefix in storage.prefixes
        assert str(e.value.args[0])


class MockStorage(AssetStorage):
    prefixes = ["s3://", "gs://"]


class MockStorageManager(StorageManager):
    _storage_providers = {
        "s3://": MockStorage,
        "gs://": MockStorage,
    }


@pytest.fixture(scope="module")
def mock_storage_manager():
    with patch('asset_pluggy.storage.storage_factory.StorageManager') as mock_manager:
        mock_manager.shared.return_value = MockStorageManager.shared()
        yield mock_manager


@pytest.fixture(scope="function")
def mock_environment(monkeypatch):
    mock_configs = {"s3://s3_bucket": "/mnt/s3",
                    "gs://gs_bucket": "/mnt/gs"}

    monkeypatch.setenv("ASSET_BUCKET_MT_CONFIG", json.dumps(mock_configs))


def test_mount_configs(mock_environment):
    configs = StorageFactory.mount_configs()
    assert len(configs) == 2
    assert isinstance(configs[0], MountConfig)
    assert configs[0].mount == "/mnt/s3"
    assert configs[1].url == "gs://gs_bucket"


def test_mount_configs_no_env(monkeypatch):
    monkeypatch.delenv("ASSET_BUCKET_MT_CONFIG", raising=False)
    assert StorageFactory.mount_configs() is None


@pytest.mark.parametrize("url, expected_mount", [
    ("s3://s3_bucket/file.txt", "/mnt/s3"),
    ("gs://gs_bucket/file.txt", "/mnt/gs"),
    ("/mnt/s3/file.txt", "/mnt/s3"),
    ("/mnt/gs/file.txt", "/mnt/gs"),
    ("http://example.com/file.txt", None),
])
def test_mount_config_for_url(mock_environment, url, expected_mount):
    config = StorageFactory.mount_config_for_url(url)
    if expected_mount:
        assert config.mount == expected_mount
    else:
        assert config is None


@pytest.mark.parametrize("url, expected_prefix", [
    ("s3://s3_bucket/file.txt", "s3://"),
    ("gs://gs_bucket/file.txt", "gs://"),
    ("/mnt/s3/file.txt", "s3://"),
    ("/mnt/gs/file.txt", "gs://")
])
def test_storage_for_mounted_url(mock_environment, url, expected_prefix):
    StorageManager.shared()._storage_providers = {
        "s3://": MockStorage,
        "gs://": MockStorage,
    }
    storage = StorageFactory.storage_for_url(url)
    if expected_prefix:
        assert isinstance(storage, MockStorage)
        assert expected_prefix in storage.prefixes
        assert storage.mount_config is not None
    else:
        # Assuming default_storage returns None or raises an exception
        assert storage is None
