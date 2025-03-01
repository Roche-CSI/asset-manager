from asset_client.contents import ContentUploader
from asset_client.asset import Asset
from asset_client.contents import Content
import pytest
import uuid
from unittest.mock import patch


@pytest.fixture(scope="module")
def uploadble_asset(client_asset) -> Asset:
    asset = client_asset
    asset.class_id = "test_asset"
    asset.top_hash = "test_asset"
    return asset


def test_not_uploaded(uploadble_asset: Asset):

    # 1. if no files are in remote bucket/path/to/test_asset
    # so local_contents should be []
    uploader = ContentUploader(contents=uploadble_asset.contents)
    committable = uploader.contents.filter(predicate=lambda x: x.can_commit)
    not_committed = uploader._not_committed(committable)
    assert len(not_committed) == len(committable)

    # make sure all content states got updated
    for content in uploadble_asset.contents:
        assert content.state == content.states.STAGED


def test_content_states(uploadble_asset: Asset):
    uploadble_asset.top_hash += str(uuid.uuid4().hex[6])
    uploader = ContentUploader(contents=uploadble_asset.contents)
    with patch.object(uploader, "_upload") as mocked:
        mocked.return_value = None
        uploader.commit_contents()

        for content in uploader.contents:
            assert content.state == Content.states.COMMITTING


def test_content_commit(client_asset: Asset):
    # uploadble_asset.top_hash += str(uuid.uuid4().hex[6:])
    uploader = ContentUploader(contents=client_asset.contents)
    uploader.commit_contents()
    for content in uploader.contents:
        assert content.state == Content.states.COMMITTED