from src.asset import Asset
from src.asset.contents import GcsContent
from src.cloud.utils import get_blob_from_url
from unittest.mock import patch
import os

INPUT_MSG = "enter the local path where this url would be mapped to:"


def create_content(asset: Asset, url, path=None):
    blob = get_blob_from_url(url)
    content = GcsContent.create(asset=asset, blob=blob)
    return content, blob


def test_create(asset: Asset):
    """asset fixture"""
    # create from src url
    url = "gs://bucket/files.zip"
    path = os.path.join(asset.repo_dir, '/files.zip')
    obj, blob = create_content(asset, url, path)
    assert obj and obj.meta["type"] == "gcs" and obj.path == os.path.relpath(path, asset.repo_dir)
    assert obj.hash_value == blob.md5_hash and obj.hash_type == "md5" and obj.content_type == blob.content_type

    # create from blob
    blob = get_blob_from_url(url)
    obj = GcsObject.create(asset=asset, object_type="gcs", blob=blob, path=path)
    assert obj and obj.object_type == "gcs" and obj.path == os.path.relpath(path, asset.repo_dir)
    assert obj.hash_value == blob.md5_hash and obj.hash_type == "md5" and obj.content_type == blob.content_type

    # create path is None
    with patch('src.asset.objects.gcs_object.get_input', return_value=path) as mocked:
        obj = GcsObject.create(asset=asset, object_type="gcs", blob=blob)
        mocked.assert_called_once_with(INPUT_MSG)
        assert obj and obj.object_type == "gcs" and obj.path == os.path.relpath(path, asset.repo_dir)
        assert obj.hash_value == blob.md5_hash and obj.hash_type == "md5" and obj.content_type == blob.content_type


def test_bulk_create(asset):
    # bulk create from dir
    url = "gs://bucket/"
    expected = os.path.join(asset.repo_dir, 'bulk_create')
    with patch('src.asset.objects.gcs_object.get_input', return_value=expected) as mocked:
        objects = GcsObject.bulk_create(asset, url)
        mocked.assert_called_once_with('enter the local directory where this url would be mapped to:')
        assert len(objects) > 0


def test_validate_path(asset: Asset):
    """asset fixture"""
    url = "gs://bucket/files.zip"
    expected = os.path.join(asset.repo_dir, 'files.zip')
    with patch('src.asset.objects.gcs_object.get_input', return_value=expected) as mocked:
        create_content(asset, url)
        mocked.assert_called_once_with(INPUT_MSG)
