import os
from tempfile import TemporaryDirectory, NamedTemporaryFile

from asset_utils.utils.path_utils import PathUtils


def test_abs_path():
    base_path = "/tmp"
    relative_path = "test"
    expected_path = os.path.join(base_path, relative_path)
    assert PathUtils.abs_path(relative_path, base=base_path) == expected_path


def test_remove_file():
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        assert os.path.exists(tmp_file_path), "Temporary file should exist before removal."
        PathUtils.remove(tmp_file_path)
        assert not os.path.exists(tmp_file_path), "Temporary file should be removed."


def test_remove_directory():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir_path = tmp_dir
        assert os.path.exists(tmp_dir_path), "Temporary directory should exist before removal."
        PathUtils.remove(tmp_dir_path)
        assert not os.path.exists(tmp_dir_path), "Temporary directory should be removed."
