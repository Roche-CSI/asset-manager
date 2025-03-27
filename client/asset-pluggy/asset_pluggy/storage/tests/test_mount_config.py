import pytest

from asset_pluggy.storage.mount_config import MountConfig
from asset_utils.common.exceptions import AssetException


@pytest.fixture
def mount_config():
    return MountConfig(mount="/mnt/data", url="s3://bucket/data")


def test_init(mount_config):
    assert mount_config.mount == "/mnt/data"
    assert mount_config.url == "s3://bucket/data"


def test_str_repr(mount_config):
    assert str(mount_config) == "MountConfig(mount=/mnt/data, url=s3://bucket/data)"
    assert repr(mount_config) == "MountConfig(mount=/mnt/data, url=s3://bucket/data)"


def test_eq_hash(mount_config):
    config1 = MountConfig("/mnt/data", "s3://bucket/data")
    config2 = MountConfig("/mnt/data", "s3://bucket/data")
    config3 = MountConfig("/mnt/other", "s3://bucket/other")

    assert config1 == config2
    assert config1 != config3
    assert hash(config1) == hash(config2)
    assert hash(config1) != hash(config3)


def test_to_dict(mount_config):
    expected = {"mount": "/mnt/data", "url": "s3://bucket/data"}
    assert mount_config.to_dict() == expected


def test_url_to_posix_valid(mount_config):
    url = "s3://bucket/data/file.txt"
    expected = "/mnt/data/file.txt"
    assert mount_config.url_to_posix(url) == expected


def test_url_to_posix_invalid(mount_config):
    invalid_url = "s3://other-bucket/data/file.txt"
    with pytest.raises(AssetException):
        mount_config.url_to_posix(invalid_url)


def test_posix_to_url_valid(mount_config):
    posix = "/mnt/data/file.txt"
    expected = "s3://bucket/data/file.txt"
    assert mount_config.posix_to_url(posix) == expected


def test_posix_to_url_invalid(mount_config):
    invalid_posix = "/other/data/file.txt"
    with pytest.raises(AssetException):
        mount_config.posix_to_url(invalid_posix)


def test_is_posix(mount_config):
    assert mount_config.is_posix("/mnt/data/file.txt") is True
    assert mount_config.is_posix("/other/data/file.txt") is False


def test_is_url(mount_config):
    assert mount_config.is_url("s3://bucket/data/file.txt") is True
    assert mount_config.is_url("s3://other-bucket/data/file.txt") is False


@pytest.mark.parametrize("mount,url", [
    ("/mnt/data", "s3://bucket/data"),
    ("/mnt/logs", "s3://logs-bucket/"),
    ("/data", "https://data.example.com"),
])
def test_multiple_configs(mount, url):
    config = MountConfig(mount, url)
    assert config.mount == mount
    assert config.url == url
    assert config.is_posix(f"{mount}/file.txt") is True
    assert config.is_url(f"{url}/file.txt") is True
