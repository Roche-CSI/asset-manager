import os
from unittest.mock import MagicMock, patch

import pytest

from asset_contents.posix_content import PosixContent
from asset_pluggy.storage.blob import StorageData
from asset_utils.common import exceptions


@pytest.fixture
def mock_blob(test_data):
    blob = MagicMock(spec=StorageData)
    blob.name = os.path.join(test_data, 'file_types/csvs/customers.csv')
    blob.content_type = "application/octet-stream"
    blob.size = 17261
    blob.get_hash.return_value = ('md5', 'DSPIdGEdaCS3U1Vi0nYprw==')
    return blob


def test_create(mock_blob):
    with patch.object(PosixContent, 'storage_system_id', return_value='posix'):
        posix_content = PosixContent.create(storage_name="posix", blob=mock_blob)

    assert posix_content.id == 'posix:md5_DSPIdGEdaCS3U1Vi0nYprw=='
    assert posix_content.hash == "md5_DSPIdGEdaCS3U1Vi0nYprw=="
    assert posix_content.hash_value == "DSPIdGEdaCS3U1Vi0nYprw=="
    assert posix_content.hash_type == "md5"
    assert posix_content.size == 17261
    assert posix_content.mime_type == "application/octet-stream"
    assert posix_content.can_download is True
    assert posix_content.can_upload is True
    assert posix_content.is_proxy is False

    # test with proxy content
    with pytest.raises(exceptions.UnSupportedOperation):
        PosixContent.create(storage_name="posix", blob=mock_blob, proxy=True)


def test_validate_path(test_data):
    PosixContent._validate_path(os.path.join(test_data, "file_types/csvs/customers.csv"))

    with pytest.raises(exceptions.InvalidObjectSourceError):
        PosixContent._validate_path(os.path.join(test_data, "non_existent_file"))


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
        assert PosixContent.compute_hash(src_path) == item.get("hash")
