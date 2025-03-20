import os

import pytest

from asset_db import AssetsDB, FileDB
from asset_db.db import Database


def test_path_singleton():
    """
    Test that each path can only have one instance of a db class
    """
    db1 = AssetsDB(path="/tmp/test_1.yaml")
    db2 = AssetsDB(path="/tmp/test_2.yaml")
    assert db1 != db2

    db3 = AssetsDB(path="/tmp/test_1.yaml")
    assert db3 == db1
    assert db3 != db2

    with pytest.raises(Exception) as e:
        FileDB(path="/tmp/test_2.yaml")
    assert str(e.value) == "Instance already exists with same path but different class type"


@pytest.fixture(scope="module")
def db(asset_root) -> Database:
    db_path = os.path.join(asset_root, "database_test", "db_file.json")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return Database(path=db_path)


def test_db_create(db: Database):
    """make sure metadb got created"""
    assert db is not None  # db instance got created
    assert db.path and os.path.exists(db.path)


def test_update(db):
    db.update(key="value")
    assert db.retrieve("key") == "value"


def test_write_and_read(db):
    Database.write({"key": "value"}, db.path)
    data = Database.read(db.path)
    assert data == {"key": "value"}


def test_retrieve(db):
    db.update(key1="value1", key2="value2")
    assert db.retrieve("key1") == "value1"
    assert db.retrieve(["key1", "key2"]) == {"key1": "value1", "key2": "value2"}
