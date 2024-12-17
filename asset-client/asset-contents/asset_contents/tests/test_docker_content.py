from unittest.mock import MagicMock

import pytest

from asset_contents import DockerContent
from asset_pluggy.storage import StorageData


@pytest.fixture
def mock_blob():
    blob = MagicMock(spec=StorageData)
    blob.content_type = 'application/vnd.docker.distribution.manifest.v2+json'
    blob.size = 1024
    blob.url = 'gcr.io/test-project/test-image@sha256:abcd1234'
    blob.get_hash.return_value = ('md5', '4N7Mr93Wbtzm5j104ol0Mw==')
    return blob


def test_create(mock_blob):
    storage_name = "gcr"

    # test with the proxy flag set to True
    docker_content = DockerContent.create(storage_name, mock_blob, proxy=True)
    assert docker_content.id == 'gcr:proxy_md5_EyoCou8v0sI0Djg0EFrnHw=='
    assert docker_content.mime_type == mock_blob.content_type
    assert docker_content.size == mock_blob.size
    assert docker_content.hash_value == '4N7Mr93Wbtzm5j104ol0Mw=='
    assert docker_content.hash_type == 'md5'
    assert docker_content.meta["type"] == 'gcr'
    assert docker_content.meta["src"] == mock_blob.url
    assert docker_content.meta["proxy"] is True
    assert docker_content.file_id == '4N7Mr93Wbtzm5j104ol0Mw=='
    assert docker_content.hash == 'md5_4N7Mr93Wbtzm5j104ol0Mw=='
    assert docker_content.is_proxy is True

    # test with the proxy flag set to False
    docker_content = DockerContent.create(storage_name, mock_blob, proxy=False)
    assert docker_content.id == 'gcr:proxy_md5_EyoCou8v0sI0Djg0EFrnHw=='
    assert docker_content.mime_type == mock_blob.content_type
    assert docker_content.size == mock_blob.size
    assert docker_content.hash_value == '4N7Mr93Wbtzm5j104ol0Mw=='
    assert docker_content.hash_type == 'md5'
    assert docker_content.meta["type"] == 'gcr'
    assert docker_content.meta["src"] == mock_blob.url
    assert docker_content.meta["proxy"] is True
    assert docker_content.file_id == '4N7Mr93Wbtzm5j104ol0Mw=='
    assert docker_content.hash == 'md5_4N7Mr93Wbtzm5j104ol0Mw=='
    assert docker_content.is_proxy is True
