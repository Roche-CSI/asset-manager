from unittest.mock import MagicMock, patch

import pytest

from asset_contents.content import Content
from asset_contents.content_set import ContentSet


@pytest.fixture
def mock_asset():
    asset = MagicMock()
    asset.repo.contents_url.return_value = "http://example.com"
    asset.top_hash = "top_hash"
    asset.contents_cache_dir = "/tmp/cache"
    asset.states_db.get_content_states.return_value = {}
    asset.content_stats_db.get_stats.return_value = {}
    return asset


@pytest.fixture
def content_set(mock_asset):
    return ContentSet(asset=mock_asset)


@pytest.fixture
def mock_content():
    content = MagicMock(spec=Content)
    content.size = 100
    content.file_id = "file_id"
    content.get_state.return_value = "state"
    content.get_content_stat.return_value = MagicMock(serialize=lambda: "serialized_stat")
    return content


def test_remote_url(content_set):
    assert content_set.remote_url == "http://example.com/top_hash"


def test_cache_dir(content_set):
    assert content_set.cache_dir == "/tmp/cache"


def test_size(content_set, mock_content):
    content_set.add(mock_content)
    assert content_set.size == 100


def test_filter(content_set, mock_content):
    content_set.add(mock_content)
    result = content_set.filter(lambda x: x.size == 100)
    assert result == [mock_content]


def test_add_content(content_set, mock_content):
    result = content_set.add_content(mock_content)
    assert result == mock_content
    assert mock_content in content_set


def test_save(content_set):
    content_set.save()
    content_set.asset.states_db.update.assert_called_once()
    content_set.asset.content_stats_db.update.assert_called_once()


def test_de_serialize(content_set, mock_content):
    with patch('asset_contents.content_factory.ContentFactory.de_serialize', return_value=mock_content):
        result = content_set.de_serialize()
        assert result == mock_content


def test_update_states(content_set, mock_content):
    content_set.add(mock_content)
    content_set.update_states(save=True)
    content_set.asset.states_db.update.assert_called_once()


def test_update_file_stats(content_set, mock_content):
    content_set.add(mock_content)
    content_set.update_file_stats(save=True)
    content_set.asset.content_stats_db.update.assert_called_once()


def test_exists(content_set, mock_content):
    content_set.add(mock_content)
    mock_content.exists.return_value = True
    assert content_set.exists() is True
