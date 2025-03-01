import pytest
import os
from asset_client.asset_class import AssetClass
from asset_client.asset import Asset
from asset_client.objects import ObjectSet
from asset_client.contents import ContentSet
from utils.file_utils import FileUtils


@pytest.fixture(scope="module")
def asset_data(test_app):
    """need the test_app fixture for making db transactions"""
    path = os.path.join(os.path.dirname(__file__), "test_data.json")
    return FileUtils.read_json(path)


def test_deserialize(asset_data):
    asset = Asset(user="user1", data=asset_data)
    assert isinstance(asset.objects, ObjectSet) and len(asset.objects) > 0
    assert isinstance(asset.contents, ContentSet) and len(asset.contents) > 0
    assert asset.asset_class and asset.asset_class.name and isinstance(asset.asset_class, AssetClass)

    assert asset