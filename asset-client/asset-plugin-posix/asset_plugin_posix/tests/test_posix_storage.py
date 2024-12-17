import os

from asset_plugin_posix.posix_storage import PosixStorage
from asset_utils.utils.file_utils import FileUtils


def test_get_blob(test_data):
    files = [
        "file_types/csvs/customers.csv",
        "file_types/jpegs/photo-1522364723953-452d3431c267.jpg",
        "file_types/jsons/web_app.json",
        "file_types/yamls/invoice.yaml",
    ]

    for file in files:
        url = os.path.join(test_data, file)
        blob = PosixStorage.shared().get_blob(url_string=url)
        assert blob.host == "file://"
        assert blob.name == url
        assert blob.content_type == FileUtils.mime_type(src=url)
        assert blob.size == os.path.getsize(url)
        assert blob.path_in_asset == os.path.basename(url)


def test_blob_exists(test_data):
    data = {
        "file_types/csvs/customers.csv": True,
        "file_types/jpegs/photo-1522364723953-452d3431c267.jpg": True,
        "file_types/jsons/web_app.json": True,
        "file_types/yamls/invoice.yaml": True,
        "file_types/csvs/invoice.csv": False,
        "file_types/jpegs/photo-1522364723953.jpg": False,
        "file_types/jsons/customers.json": False,
        "file_types/yamls/web_app.yaml": False,
    }

    for path, expected in data.items():
        url = os.path.join(test_data, path)
        exists = PosixStorage.shared().blob_exists(url_string=url)
        assert exists is expected


def test_list_blobs(test_data):
    data = [
        {"path": "file_types/csvs", "count": 2},
        {"path": "file_types/yamls", "count": 3},
        {"path": "file_types", "count": 8},
        {"path": "file_types", "ignore": "*.yml", "count": 7},
        {"path": "file_types", "ignore": "*.yaml,*.yml", "count": 5},
        {"path": "file_types", "ignore": "*.csv", "count": 6},
        {"path": "file_types", "ignore": "*.csv,*.jpg", "count": 4},
    ]

    for item in data:
        url = os.path.join(test_data, item.get("path"))
        blobs = PosixStorage.shared().list_blobs(url=url, ignore=item.get("ignore"))
        assert len(blobs) == item.get("count")


def test_url_is_file(test_data):
    data = {
        "file_types/csvs/customers.csv": True,
        "file_types/jpegs/photo-1522364723953-452d3431c267.jpg": True,
        "file_types/jsons/web_app.json": True,
        "file_types/yamls/invoice.yaml": True,
        "file_types/csvs": False,
        "file_types/jpegs": False,
        "file_types/jsons": False,
        "file_types/yamls": False,
    }

    for path, expected in data.items():
        url = os.path.join(test_data, path)
        is_file = PosixStorage.shared().url_is_file(url)
        assert is_file is expected
