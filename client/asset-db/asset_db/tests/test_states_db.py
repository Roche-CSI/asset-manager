import os

import pytest

from asset_db import StatesDB

DATA = {
    "test_data/2.txt": "pending",
    "test_data/imgs/photo-1493976040374-85c8e12f0c0e.jpg": "uploaded",
    "test_data/imgs/photo-1504198453319-5ce911bafcde.jpg": "pending",
    "test_data/imgs/photo-1507143550189-fed454f93097.jpg": "uploading",
    "test_data/imgs/photo-1513938709626-033611b8cc03.jpg": "version",
    "test_data/imgs/photo-1516117172878-fd2c41f4a759.jpg": "versioned",
    "test_data/imgs/photo-1516972810927-80185027ca84.jpg": "committing",
    "test_data/imgs/photo-1522364723953-452d3431c267.jpg": "committed",
    "test_data/imgs/photo-1524429656589-6633a470097c.jpg": "renaming",
    "test_data/imgs/photo-1530122037265-a5f1f91d3b99.jpg": "renamed",
}


@pytest.fixture(scope="module")
def states_db(asset_root):
    os.makedirs(os.path.join(asset_root, "states_db_test"))
    return StatesDB(path=os.path.join(asset_root, "states_db_test", "states.yaml"))


def test_add_states(states_db):
    # create a directory
    states_db.add_object_states(**DATA)
    stored = states_db.get_object_states()
    assert stored == DATA


def test_remove_states(states_db):
    data = DATA.copy()
    states_db.add_object_states(**data)
    data.pop("test_data/2.txt")
    states_db.remove_object_states(["test_data/2.txt"])
    stored = states_db.get_object_states()
    assert data == stored
