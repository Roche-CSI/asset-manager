import os

import pytest

from asset_db.assets_db import AssetsDB


@pytest.fixture(scope="module")
def db(asset_root) -> AssetsDB:
    db_path = os.path.join(asset_root, "database_test", "meta_hashes.json")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return AssetsDB(path=db_path)


def test_db_create(db: AssetsDB):
    """make sure metadb got created"""
    assert db is not None  # db instance got created
    assert db.path and os.path.exists(db.path)


def test_add_file_hash(db: AssetsDB):
    path = "test/path"
    hash = "abc123"
    db.add_file_hash(path, hash)
    assert db.file_hashes[path] == hash, "File hash should be added to the database"


def test_remove_files(db: AssetsDB):
    # Setup - add some file hashes
    paths = ["test/path1", "test/path2"]
    hashes = ["abc123", "def456"]
    for path, hash in zip(paths, hashes):
        db.add_file_hash(path, hash)

    # Test removing one file
    db.remove_files(paths[0])
    assert paths[0] not in db.file_hashes, "File should be removed from the database"
    assert paths[1] in db.file_hashes, "Other files should remain in the database"
