import json
from unittest.mock import patch, MagicMock

import pytest

from asset_core.server.asset_server import AssetServer


@pytest.fixture
def asset_server():
    return AssetServer()


def test_create_asset(asset_server):
    with patch.object(asset_server, 'post', return_value=MagicMock(content=json.dumps({"id": "123"}))):
        result = asset_server.create_asset(name="test_asset")
        assert result["id"] == "123"


def test_create_asset_class(asset_server):
    with patch.object(asset_server, 'post', return_value=MagicMock(content=json.dumps({"id": "123"}))):
        result = asset_server.create_asset_class(name="test_class")
        assert result["id"] == "123"


def test_update_asset(asset_server):
    with patch.object(asset_server, 'put', return_value=MagicMock(content=json.dumps({"status": "success"}))):
        result = asset_server.update_asset(id="123", data={"name": "updated_asset"})
        assert result["status"] == "success"


def test_update_refs(asset_server):
    with patch.object(asset_server, 'post', return_value=MagicMock(content=json.dumps({"status": "success"}))):
        result = asset_server.update_refs(data={"ref": "new_ref"})
        assert result["status"] == "success"


def test_find_refs(asset_server):
    with patch.object(asset_server, 'get', return_value=MagicMock(content=json.dumps([{"ref": "test_ref"}]))):
        result = asset_server.find_refs(asset_name="test_asset", project_id="proj_123")
        assert result[0]["ref"] == "test_ref"


def test_commit_asset(asset_server):
    with patch.object(asset_server, 'put', return_value=MagicMock(content=json.dumps({"status": "committed"}))):
        result, status_code = asset_server.commit_asset(id="123", data={"key": "value"}, message="commit message")
        assert result["status"] == "committed"


def test_get_asset_yaml(asset_server):
    with patch.object(asset_server, 'get', return_value=MagicMock(content=json.dumps({"yaml": "content"}))):
        result = asset_server.get_asset_yaml(id="123")
        assert result["yaml"] == "content"


def test_get_asset(asset_server):
    with patch.object(asset_server, 'get', return_value=MagicMock(content=json.dumps({"id": "123"}))):
        result = asset_server.get_asset(id="123")
        assert result["id"] == "123"


def test_find_asset_versions(asset_server):
    with patch.object(asset_server, 'get', return_value=MagicMock(content=json.dumps([{"version": "v1"}]))):
        result = asset_server.find_asset_versions(project_id="proj_123", version_names=["v1"])
        assert result[0]["version"] == "v1"


def test_get_version(asset_server):
    with patch.object(asset_server, 'get', return_value=MagicMock(content=json.dumps([{"version": "v1"}]))):
        result = asset_server.get_version(project_id="proj_123", class_id="class_123", seq_id="seq_123")
        assert result["version"] == "v1"


def test_update_asset_class(asset_server):
    with patch.object(asset_server, 'put', return_value=MagicMock(content=json.dumps({"status": "updated"}))):
        asset_server.update_asset_class(id="123", data={"name": "updated_class"})
        # No assertion needed as the method does not return anything
