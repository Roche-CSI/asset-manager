import os
from tempfile import TemporaryDirectory

import pytest

from asset_core.asset.asset_ignore import AssetIgnore


@pytest.fixture
def temp_files():
    with TemporaryDirectory() as temp_dir:
        file_paths = [
            os.path.join(temp_dir, "file1.txt"),
            os.path.join(temp_dir, "file2.txt"),
            os.path.join(temp_dir, "file3.log"),
            os.path.join(temp_dir, "file4.txt"),
            os.path.join(temp_dir, "dir1", "file5.txt"),
            os.path.join(temp_dir, "dir1", "file6.log"),
        ]
        os.makedirs(os.path.join(temp_dir, "dir1"), exist_ok=True)
        for file_path in file_paths:
            with open(file_path, 'w') as f:
                f.write("test content")
        yield file_paths, temp_dir


def test_filtered_paths(temp_files):
    file_paths, temp_dir = temp_files

    # Test No Ignore Patterns
    asset_ignore = AssetIgnore(temp_dir)
    result = asset_ignore.filtered_paths(file_paths)
    assert result == file_paths, "All files should be returned when there are no ignore patterns"

    # Test With Ignore Patterns
    ignore_file_path = os.path.join(temp_dir, ".assetignore")
    with open(ignore_file_path, 'w') as f:
        f.write("*.txt\n")  # Ignore all .txt files
    asset_ignore = AssetIgnore(temp_dir)
    result = asset_ignore.filtered_paths(file_paths)
    expected = [file for file in file_paths if not file.endswith(".txt")]
    assert result == expected, "Files matching the ignore patterns should be filtered out"


def test_ignored_paths(temp_files):
    file_paths, temp_dir = temp_files

    # Test No Ignore Patterns
    asset_ignore = AssetIgnore(temp_dir)
    result = asset_ignore.ignored_paths(file_paths)
    assert result == [], "No files should be ignored when there are no ignore patterns"

    # Test With Ignore Patterns
    ignore_file_path = os.path.join(temp_dir, ".assetignore")
    with open(ignore_file_path, 'w') as f:
        f.write("*.txt\n")  # Ignore all .txt files
    asset_ignore = AssetIgnore(temp_dir)
    result = asset_ignore.ignored_paths(file_paths)
    expected = [file for file in file_paths if file.endswith(".txt")]
    assert result == expected, "Files matching the ignore patterns should be identified"
