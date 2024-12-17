import pytest

from asset_core.asset.status_enums import StatusEnums
from asset_utils.common.exceptions import AssetException


def test_from_string_with_numeric_string():
    assert StatusEnums.from_string("1") == StatusEnums.PUBLIC
    assert StatusEnums.from_string("2") == StatusEnums.PRIVATE
    assert StatusEnums.from_string("3") == StatusEnums.DELETED
    assert StatusEnums.from_string("4") == StatusEnums.DEPRECATED
    assert StatusEnums.from_string("5") == StatusEnums.OBSOLETE


def test_from_string_with_status_name():
    assert StatusEnums.from_string("Public") == StatusEnums.PUBLIC
    assert StatusEnums.from_string("Private") == StatusEnums.PRIVATE
    assert StatusEnums.from_string("Deleted") == StatusEnums.DELETED
    assert StatusEnums.from_string("Deprecated") == StatusEnums.DEPRECATED
    assert StatusEnums.from_string("Obsolete") == StatusEnums.OBSOLETE


def test_from_string_with_invalid_value():
    with pytest.raises(AssetException):
        StatusEnums.from_string("Invalid")


def test_default():
    assert StatusEnums.default() == StatusEnums.PUBLIC
