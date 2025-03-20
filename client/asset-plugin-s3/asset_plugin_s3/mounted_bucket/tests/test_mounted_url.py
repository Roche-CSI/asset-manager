import pytest

from asset_pluggy.storage import BlobStoreURL
from asset_pluggy.storage.mount_config import MountConfig
from asset_plugin_s3.mounted_bucket.mounted_url import MountedBlobStoreURL
from asset_utils.common import exceptions


class MockBlobStoreURL(BlobStoreURL):
    def __init__(self, url: str, **kwargs):
        self.url = url
        self.kwargs = kwargs


@pytest.fixture
def mount_config():
    return MountConfig(mount="/mnt/data", url="s3://bucket/data")


@pytest.fixture
def mock_blob_store_url(monkeypatch):
    monkeypatch.setattr('asset_plugin_s3.mounted_bucket.mounted_url.MountedBlobStoreURL', MockBlobStoreURL)


@pytest.mark.usefixtures("mock_blob_store_url")
class TestMountedBlobStoreURL:

    def test_init_with_posix_path(self, mount_config):
        posix_path = "/mnt/data/file.txt"
        url = MountedBlobStoreURL(posix_path, mount_cfg=mount_config)
        assert url.posix_url == posix_path
        assert url.url == "s3://bucket/data/file.txt"

    def test_init_with_url(self, mount_config):
        s3_url = "s3://bucket/data/file.txt"
        url = MountedBlobStoreURL(s3_url, mount_cfg=mount_config)
        assert url.posix_url == "/mnt/data/file.txt"
        assert url.url == s3_url

    def test_str_representation(self, mount_config):
        url = MountedBlobStoreURL("/mnt/data/file.txt", mount_cfg=mount_config)
        expected_str = "MountedBlobStoreURL(url=s3://bucket/data/file.txt, path=/mnt/data/file.txt)"
        assert str(url) == expected_str

    def test_init_without_mount_cfg(self):
        with pytest.raises(KeyError):
            MountedBlobStoreURL("s3://bucket/data/file.txt")

    def test_init_with_outside_posix_path(self, mount_config):
        url = MountedBlobStoreURL("/tmp/file.txt", mount_cfg=mount_config)
        assert url.posix_url == "/tmp/file.txt"
        assert url.url == "/tmp/file.txt"

    def test_init_with_invalid_url(self, mount_config):
        with pytest.raises(exceptions.AssetException):
            MountedBlobStoreURL("s3://invalid-bucket/data/file.txt", mount_cfg=mount_config)

    def test_kwargs_passed_to_parent(self, mount_config):
        extra_kwarg = {"ignore": "value"}
        url = MountedBlobStoreURL("/mnt/data/file.txt", mount_cfg=mount_config, **extra_kwarg)
        # should throw a error since extra is not a valid argument for MockBlobStoreURL
        for key in extra_kwarg:
            assert getattr(url, key) == extra_kwarg[key]

    @pytest.mark.parametrize("input_path,expected_url,expected_posix", [
        ("/mnt/data/file1.txt", "s3://bucket/data/file1.txt", "/mnt/data/file1.txt"),
        ("s3://bucket/data/file2.txt", "s3://bucket/data/file2.txt", "/mnt/data/file2.txt"),
        ("/mnt/data/nested/file3.txt", "s3://bucket/data/nested/file3.txt", "/mnt/data/nested/file3.txt"),
    ])
    def test_various_inputs(self, mount_config, input_path, expected_url, expected_posix):
        url = MountedBlobStoreURL(input_path, mount_cfg=mount_config)
        assert url.url == expected_url
        assert url.posix_url == expected_posix
