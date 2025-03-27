import os

import pytest

from asset_db.file_db import FileDB


@pytest.fixture(scope="module")
def db(asset_root) -> FileDB:
    db_path = os.path.join(asset_root, "database_test", "file_stats.json")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return FileDB(path=db_path)


def test_db_create(db: FileDB):
    """make sure metadb got created"""
    assert db is not None  # db instance got created
    assert db.path and os.path.exists(db.path)


def test_add_and_get_stats(db):
    db.add_stats(file1="hash1", file2="hash2")
    stats = db.get_stats()
    assert stats == {"file1": "hash1", "file2": "hash2"}, "Stats should be correctly added and retrieved"


def test_remove_stats(db):
    db.add_stats(file1="hash1", file2="hash2")
    db.remove_stats(["file1"])
    stats = db.get_stats()
    assert "file1" not in stats, "file1 should be removed from stats"
    assert "file2" in stats, "file2 should remain in stats"
