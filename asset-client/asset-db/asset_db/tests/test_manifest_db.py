import os

import pytest

from asset_db import ManifestDB


@pytest.fixture(scope="module")
def db(asset_root) -> ManifestDB:
    db_path = os.path.join(asset_root, "database_test", "manifest.yaml")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return ManifestDB(path=db_path)


def test_db_create(db: ManifestDB):
    """make sure metadb got created"""
    assert db is not None  # db instance got created
    assert db.path and os.path.exists(db.path)


def test_add_objects(db: ManifestDB):
    objects = {"1": {"name": "test_object1"}, "2": {"name": "test_object2"}}
    db.add_objects(**objects)
    result = db.get_objects()
    assert result == objects


def test_get_objects(db: ManifestDB):
    objects = {"objects": {"1": {"name": "test_object1"}, "2": {"name": "test_object2"}}}
    db.update(**objects)
    result = db.get_objects()
    assert result == objects["objects"]


def test_get(db: ManifestDB):
    data = {"key1": "value1", "key2": "value2"}
    db.update(**data)
    result = db.get("key1")
    assert result == "value1"


def test_remove_objects(db: ManifestDB):
    objects = {"objects": {"1": {"name": "test_object1"}, "2": {"name": "test_object2"}}}
    db.update(**objects)
    db.remove_objects(["1"])
    result = db.get_objects()
    assert "1" not in result
    assert "2" in result


def test_clear_objects(db: ManifestDB):
    objects = {"objects": {"1": {"name": "test_object1"}, "2": {"name": "test_object2"}}}
    db.update(**objects)
    db.clear_objects()
    result = db.get_objects()
    assert result == {}
