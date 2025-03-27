import os

import pytest

from asset_contents.file_stat import FileStat


@pytest.fixture
def test_items():
    return [
        {
            "src": "file_types/csvs/customers.csv",
            "num_links": 1,
            "size": 17261,
        },
        {
            "src": "file_types/jpegs/photo-1522364723953-452d3431c267.jpg",
            "num_links": 1,
            "size": 12853831,
        },
        {
            "src": "file_types/yamls/invoice.yaml",
            "num_links": 1,
            "size": 547,
        },
    ]


def test_filestat_init(test_data, test_items):
    for item in test_items:
        file_path = os.path.join(test_data, item["src"])
        # initialize file stat object with file path and file id
        file_stat = FileStat(src=file_path)
        assert file_stat.num_links == item["num_links"]
        assert file_stat.size == item["size"]


def test_serialize(test_data, test_items):
    for item in test_items:
        file_path = os.path.join(test_data, item["src"])
        # serialize file stat object to dictionary
        file_data = FileStat(src=file_path).serialize()
        assert file_data["num_links"] == item["num_links"]
        assert file_data["size"] == item["size"]


def test_deserialize(test_items):
    for item in test_items:
        # deserialize dictionary to file stat object
        file_stat = FileStat.de_serialize(item)
        assert file_stat.num_links == item["num_links"]
        assert file_stat.size == item["size"]
