import os
from unittest.mock import patch, MagicMock

import pytest

from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_plugin_gcs.gcs_blob import GcsBlob
from asset_plugin_gcs.gcs_storage import GcsStorage
from asset_utils.utils.file_utils import FileUtils


def mock_download_file(self, file_url, dst, force=False):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    test_file = os.path.join(root_dir, "test_data/asset_classes", os.path.basename(file_url))
    FileUtils.copy_file(src=test_file, dst=dst)


def test_download_class_list(store):
    with patch.object(AssetFetcher, "download_file", new=mock_download_file):
        fetcher = AssetFetcher(store=store)
        class_list = fetcher.download_class_list()
    assert os.path.exists(class_list)
    data = FileUtils.read_yaml(class_list)
    assert len(data.keys()) > 0


def test_download_asset_class(store):
    class_id = "3350b6d5-ded4-4ccf-adab-d5b6b8920041"
    with patch.object(AssetFetcher, "download_file", new=mock_download_file):
        fetcher = AssetFetcher(store=store)
        class_yaml = fetcher.download_asset_class(class_id)
    assert os.path.exists(class_yaml)
    data = FileUtils.read_yaml(class_yaml)
    assert data.get('id') == class_id


@pytest.fixture
def mock_alias_blobs():
    blob = MagicMock(spec=GcsBlob)
    blob.content_type = "yaml"
    blob.size = 310
    blob.name = "1234567-6f0b-4405-a452-270d24e374d5__1__test_mock_alias.yaml"
    blob.get_hash.return_value = ('md5', '1234567890amazing==')
    return [blob]


def test_get_seq_id_from_bucket(store, mock_alias_blobs):
    class_id = "3350b6d5-ded4-4ccf-adab-d5b6b8920041"
    alias = "test_mock_alias"
    fetcher = AssetFetcher(store=store)
    with patch.object(GcsStorage, "list_blobs", return_value=mock_alias_blobs):
        seq_id = fetcher.get_seq_id_from_bucket(class_id, alias)
        assert seq_id == "1"


def test_get_asset_class_id(store):
    test_items = {
        "test_rnn": "7969a9b4-88d8-448b-9fd8-f104253ac27c",
        "group_test": "3350b6d5-ded4-4ccf-adab-d5b6b8920041",
    }
    fetcher = AssetFetcher(store=store)
    with patch.object(AssetFetcher, "download_file", new=mock_download_file):
        fetcher.download_class_list()
        for class_name, expected_id in test_items.items():
            got_id = fetcher.get_asset_class_id(class_name)
            assert got_id == expected_id
