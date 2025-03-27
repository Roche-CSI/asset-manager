from unittest.mock import MagicMock

import pytest

from asset_contents import ContentSet, Content
from asset_contents.content_uploader import ContentUploader
from asset_pluggy.storage import StorageData
from asset_pluggy.storage.storage_factory import AssetStorage


@pytest.fixture
def mock_blob():
    blob = MagicMock(spec=StorageData)
    blob.name = "test/4N7Mr93Wbtzm5j104ol0Mw=="
    return blob


@pytest.fixture
def mock_storage():
    blob = MagicMock(spec=StorageData)
    blob.name = "test/4N7Mr93Wbtzm5j104ol0Mw=="
    storage = MagicMock(spec=AssetStorage)
    storage.list_blobs.return_value = [blob]
    return storage


@pytest.fixture
def content_set():
    contents = MagicMock(spec=ContentSet)
    contents.remote_url = "gs://test_bucket/test/"
    return contents


@pytest.fixture
def target_contents():
    content1 = MagicMock(spec=Content)
    content1.file_id = '4N7Mr93Wbtzm5j104ol0Mw=='

    content2 = MagicMock(spec=Content)
    content2.file_id = '+SPIdGEdaCS3U1Vi0nYprw=='
    content2.can_stage = True

    return [content1, content2]


def test_not_uploaded(mock_blob, content_set, target_contents):
    uploader = ContentUploader(contents=content_set)
    mock_storage = MagicMock(spec=AssetStorage)

    # no blobs in the remote storage
    mock_storage.list_blobs.return_value = []
    local_contents = uploader._not_uploaded(targets=target_contents, storage=mock_storage)
    assert len(local_contents) == 2
    uploader.contents.update_states.assert_not_called()

    # one blob are in the remote storage
    mock_storage.list_blobs.return_value = [mock_blob]
    local_contents = uploader._not_uploaded(targets=target_contents, storage=mock_storage)
    assert len(local_contents) == 1
    local_contents[0].set_state.assert_not_called()
    committed_content = target_contents[0]
    committed_content.set_state.assert_called_once_with(committed_content.states.COMMITTED)
    uploader.contents.update_states.assert_called_once_with(contents=[committed_content], save=True)
