import json
import os
import pytest
from server_core.utils.file_utils import FileUtils
from server_core.utils import time_it


@pytest.fixture(scope="module")
def asset_data(test_user, test_asset_class):
    json_data = FileUtils.read_json(os.path.join(os.path.dirname(__file__), "from_client.json"))
    json_data["asset_class"] = test_asset_class.to_dict()
    from_client = {
        "user": test_user.username,
        "payload": json_data,
        "bucket_sync": True
    }
    return from_client

@pytest.fixture(scope="module")
def large_asset_data(test_user, asset_data):
    objects_data = FileUtils.read_json(os.path.join(os.path.dirname(__file__), "genia_data.json"))
    asset_data["payload"]["objects"] = objects_data
    return asset_data


def test_asset_post(test_app, asset_data):
    """has an asset record so should return a list"""
    res = test_app.post('/asset_commit',
                        follow_redirects=True,
                        data=json.dumps(asset_data))
    assert res.status_code == 405  # not allowed


def test_asset_put(test_app, asset_data):
    """has an asset record so should return a list"""
    res = test_app.put(f'/asset_commit/{asset_data.get("payload").get("id")}',
                       follow_redirects=True,
                       data=json.dumps(asset_data))
    assert res.status_code == 200  # not allowed
    data = json.loads(res.data)
    print(data)


def test_profile_large_asset(test_app, large_asset_data):
    with time_it("large_asset"):
        res = test_app.put(f'/asset_commit/{large_asset_data.get("payload").get("id")}',
                           follow_redirects=True,
                           data=json.dumps(large_asset_data))
        assert res.status_code == 200  # not allowed
        data = json.loads(res.data)
        assert "id" in data
        assert "asset_class" in data
        assert "version" in data
