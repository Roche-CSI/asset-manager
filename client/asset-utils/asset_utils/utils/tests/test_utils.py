import os.path
from datetime import datetime

from pytz import timezone

from asset_utils.utils.utils import contains_special_chars, is_integer, convert_to_pst, date_to_string, time_now, \
    string_to_timestamp, relative_path, remove_prefix, remove_suffix, list_files, find_pattern


def test_contains_special_chars():
    assert contains_special_chars("valid_string") is False
    assert contains_special_chars("invalid_string!") is True


def test_is_integer():
    assert is_integer("10") is True
    assert is_integer("10.5") is False
    assert is_integer("not_a_number") is False


def test_convert_to_pst():
    utc_time = datetime(2020, 1, 1, 12, 0, tzinfo=timezone('UTC'))
    pst_time = "2020/01/01 04-00-00 -0800"
    assert convert_to_pst(utc_time) == pst_time


def test_date_to_string():
    test_date = datetime(2020, 1, 1, 12, 0)
    assert date_to_string(test_date) == "2020/01/01 12-00-00 "


def test_string_to_timestamp():
    now = time_now()
    pst_now = convert_to_pst(now)
    converted = string_to_timestamp(pst_now)
    assert now.timestamp() == converted


def test_relative_path():
    # Assuming the function is in a file located at /path/to/your/project/utils/utils.py
    assert relative_path("/path/to/your/project/utils", "/path/to/your") == "project/utils"


def test_remove_prefix():
    assert remove_prefix("TestString", "Test") == "String"
    assert remove_prefix("SomeString", "NonExisting") == "SomeString"


def test_remove_suffix():
    assert remove_suffix("TestString", "String") == "Test"
    assert remove_suffix("SomeString", "NonExisting") == "SomeString"


def test_find_pattern():
    assert find_pattern("example*") == "*"
    assert find_pattern("test?") == "?"
    assert find_pattern("list[item]") == "[item]"
    assert find_pattern("example") is None
    assert find_pattern("*example") == "*example"
    assert find_pattern("*?*") == "*?*"


def test_list_files(project_root, test_data):
    locations = [
        (project_root, "*.py", True, ".py"),
        (os.path.join(project_root, "test_data"), "imgs", False),
        (os.path.join(project_root, "test_data"), "imgs*", True, ".jpg"),
    ]

    for path in locations:
        files_list = list_files(root_dir=path[0], pattern=path[1])
        if not path[2]:
            assert len(files_list) == 0
        else:
            for file_path in files_list:
                assert os.path.splitext(file_path)[1] == path[3]
