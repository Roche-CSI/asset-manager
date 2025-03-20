import fnmatch
import os

import pytest

from asset_core.asset import Asset
from asset_core.objects import Object
from asset_core.objects.object_factory import ObjectFactory
from asset_core.plugins import list_files, exceptions


def test_cached_objects_v2(project_root):
    objects_dir = os.path.join(project_root, "test_data/zips")
    objects = Asset(load=False).cached_objects_v2(dir=objects_dir)
    assert len(objects)


def test_data_types(asset):
    # check if it got saved
    data = asset.db.data()
    for key in Asset.serialize_fields():
        if data[key]:
            if key != 'seq_id':
                assert type(data[key]) is Asset.serialize_fields()[key]
            else:
                assert Asset.is_temp_seq_id(data[key])


def test_serialize(asset):
    for obj in asset.objects:
        assert hasattr(obj, "id") and getattr(obj, "id") is not None
    # serialize and make sure
    data = asset.serialize()
    assert isinstance(data, dict)
    for obj in data.get("objects"):
        assert "id" in obj
        assert type(obj) is dict


def test_filter_objects(asset: Asset):
    pending = asset.objects.filter(predicate=lambda x: x.get_state() in [Object.states.PENDING])
    assert len(pending) > 0
    for obj in pending:
        assert obj.get_state() == obj.states.PENDING

    jpgs = asset.objects.filter(predicate=lambda x: fnmatch.fnmatch(x.path, "*f*.jpg"))
    assert len(jpgs) == 1


def test_add_get_assets(empty_asset, test_data):
    """using repo and test_data fixture from conftest"""
    files = list_files(root_dir=test_data)
    # create a tuple of abs and relative paths
    sources = ObjectFactory().parse_sources(repo_dir=str(empty_asset.repo),
                                            targets=files,
                                            dest_dir=None)
    empty_asset.create_and_add_objects(sources)
    # get assets and check
    for obj in empty_asset.objects:
        assert obj.linked_path in files
        assert obj.get_state() == obj.states.PENDING


def test_add_proxy_content(empty_asset, test_data):
    files = list_files(root_dir=test_data)
    # create a tuple of abs and relative paths
    sources = ObjectFactory().parse_sources(repo_dir=str(empty_asset.repo),
                                            targets=files,
                                            dest_dir=None)
    # add as proxy, should raise error
    with pytest.raises(exceptions.UnSupportedOperation) as e:
        empty_asset.create_and_add_objects(sources, proxy=True)
    assert e.value.msg == "proxy assets can only be created from remote sources"
