import os.path
from unittest.mock import MagicMock, patch

import pytest

from asset_contents import BlobStoreContent
from asset_pluggy.storage import StorageData


@pytest.fixture
def mock_blob():
    blob = MagicMock(spec=StorageData)
    blob.content_type = "image/jpeg"
    blob.size = 1024
    blob.url = "gs://test_bucket/test/file_1.jpg"
    blob.get_hash.return_value = ('md5', '4N7Mr93Wbtzm5j104ol0Mw==')
    return blob


def test_create(mock_blob):
    proxy = True
    storage_name = 'gs'
    with patch.object(BlobStoreContent, 'storage_system_id', return_value='gs'):
        result = BlobStoreContent.create(storage_name, mock_blob, proxy)

    assert isinstance(result, BlobStoreContent)
    assert result.id == 'gs:proxy_md5_wqTgKEYlqi2BSdCihnhDkQ=='
    assert result.mime_type == mock_blob.content_type
    assert result.size == mock_blob.size
    assert result.hash_value == '4N7Mr93Wbtzm5j104ol0Mw=='
    assert result.hash_type == "md5"
    assert result.meta["type"] == 'gs'
    assert result.meta["src"] == mock_blob.url
    assert result.meta["proxy"] == proxy
    assert result.storage_name == storage_name
    assert result.source_url == mock_blob.url
    assert result.remote_url == mock_blob.url
    assert result.can_download is True
    assert result.can_upload is False


def test_compute_hash(test_data):
    test_items = [
        {
            'src': 'file_types/jpegs/photo-1522364723953-452d3431c267.jpg',
            'hash': ('md5', '4N7Mr93Wbtzm5j104ol0Mw==')
        },
        {
            'src': 'file_types/csvs/customers.csv',
            'hash': ('md5', '+SPIdGEdaCS3U1Vi0nYprw==')
        },
    ]

    for item in test_items:
        src_path = os.path.join(test_data, item.get("src"))
        assert BlobStoreContent.compute_hash(src_path) == item.get("hash")
