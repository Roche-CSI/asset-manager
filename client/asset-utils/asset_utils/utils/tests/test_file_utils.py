import os
import tempfile

from asset_utils.utils import list_files, time_it
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.stat_utils import FIELDS


def test_read_json_zip_dir(project_root):
    with time_it("large-asset"):
        test_dir = os.path.join(project_root, "test_data/zips")
        data = FileUtils.read_json_zip_dir(test_dir)
        assert data


def test_hardlink_directories(test_data):
    temp_dir = tempfile.mkdtemp()
    FileUtils.hardlink_directories(src_dir=test_data, dst_dir=temp_dir)
    linked = list_files(temp_dir)
    source_files = list_files(test_data)
    for file in source_files:
        target = os.path.join(temp_dir, os.path.relpath(file, test_data))
        assert target in linked and os.path.samefile(file, target)


def test_mime_type():
    path = "test_data/acm_data/wv1.4e14_0.0065/chunked_raw_data/chunk0000/raw/oc_calibration.h5"
    mime = FileUtils.mime_type(path)
    assert mime == 'application/x-hdf5'


def test_read_yaml_multi(test_data):
    files = list_files(test_data, pattern="*.yaml")
    data = FileUtils.read_yamls_multi(files)
    for file in files:
        assert file in data
        assert data[file] is not None


def test_file_stat(test_data):
    files = list_files(test_data)
    for file in files:
        stats = FileUtils.file_stat(file)
        for field in FIELDS:
            assert field in stats


def test_get_mount(project_root):
    test_data = os.path.join(project_root, "test_data", "file_cloning")
    path = os.path.join(test_data, "data.json")
    mount = FileUtils.get_mount(path)
    assert mount == "/"


def test_file_hash(test_data):
    expected = [
        {"path": "yamls/model.yml",
         "hashes": {'md5': 'l6BTlxCz4Y2ZfKapM248BQ==', 'crc32c': 'MF40IQ=='}},
        {"path": "yamls/invoice.yaml",
         "hashes": {'md5': 'XBo9UIOoHdGK4GLx+piBiA==', 'crc32c': 'Z/KSgw=='}},
        {"path": "zips/zip1.zip",
         "hashes": {'md5': '+tPd1XaMacUsFSNC5CyhbQ==', 'crc32c': 'MS9fRA=='}},
        {"path": "zips/zip2.zip",
         "hashes": {'md5': '+tPd1XaMacUsFSNC5CyhbQ==', 'crc32c': 'MS9fRA=='}},
    ]

    for file in expected:
        file_path = os.path.join(test_data, file["path"])
        md5_hash = FileUtils.file_hash(abs_path=file_path, hash_type="md5")
        assert md5_hash[1] == file["hashes"]["md5"]

        crc32c_hash = FileUtils.file_hash(abs_path=file_path, hash_type="crc32c")
        assert crc32c_hash[1] == file["hashes"]["crc32c"]


def test_bytes_hash(test_data):
    expected = [
        {"path": "yamls/model.yml",
         "hashes": {'md5': 'l6BTlxCz4Y2ZfKapM248BQ==', 'crc32c': 'MF40IQ=='}},
        {"path": "yamls/invoice.yaml",
         "hashes": {'md5': 'XBo9UIOoHdGK4GLx+piBiA==', 'crc32c': 'Z/KSgw=='}},
        {"path": "zips/zip1.zip",
         "hashes": {'md5': '+tPd1XaMacUsFSNC5CyhbQ==', 'crc32c': 'MS9fRA=='}},
        {"path": "zips/zip2.zip",
         "hashes": {'md5': '+tPd1XaMacUsFSNC5CyhbQ==', 'crc32c': 'MS9fRA=='}},
    ]

    for file in expected:
        file_path = os.path.join(test_data, file["path"])
        with open(file_path, 'rb') as f:
            data = f.read()
            md5_hash = FileUtils.bytes_hash(file_bytes=data, hash_type="md5")
            assert md5_hash[1] == file["hashes"]["md5"]

            crc32c_hash = FileUtils.bytes_hash(file_bytes=data, hash_type="crc32c")
            assert crc32c_hash[1] == file["hashes"]["crc32c"]
