import pytest
from typing import Dict, Any, Union, List
from server_core.elastic.stringify_dict import StringifyDict


def test_prepare_value_primitives():
    """Test _prepare_value with primitive types"""
    sd = StringifyDict()
    assert sd._prepare_value(None) == ""
    assert sd._prepare_value(123) == "123"
    assert sd._prepare_value(1.23) == "1.23"
    assert sd._prepare_value(True) == "True"
    assert sd._prepare_value(False) == "False"
    assert sd._prepare_value("hello") == "hello"
    assert sd._prepare_value(0) == "0"
    assert sd._prepare_value(0.0) == "0.0"


def test_prepare_value_lists():
    """Test _prepare_value with lists and tuples"""
    sd = StringifyDict()
    # Simple lists
    assert sd._prepare_value([1, 2, 3]) == ["1", "2", "3"]
    assert sd._prepare_value((1, 2, 3)) == ["1", "2", "3"]

    # Mixed lists
    assert sd._prepare_value([1, None, True, "text"]) == ["1", "", "True", "text"]

    # Nested lists
    assert sd._prepare_value([[1, None], [True, 2]]) == [["1", ""], ["True", "2"]]

    # Empty lists
    assert sd._prepare_value([]) == []
    assert sd._prepare_value(()) == []


def test_prepare_value_dicts():
    """Test _prepare_value with dictionaries"""
    sd = StringifyDict()
    # Simple dict
    input_dict = {"a": 1, "b": True, "c": None}
    expected = {"a": "1", "b": "True", "c": ""}
    assert sd._prepare_value(input_dict) == expected

    # Nested dict
    input_dict = {"a": {"b": 1, "c": None}, "d": True}
    expected = {"a": {"b": "1", "c": ""}, "d": "True"}
    assert sd._prepare_value(input_dict) == expected


def test_remove_null_dicts():
    """Test _remove_null with dictionaries"""
    sd = StringifyDict()
    # Simple dict
    assert sd._remove_null({"a": 1, "b": None}) == {"a": 1}

    # Nested dict
    input_dict = {
        "a": {"b": None, "c": 1},
        "d": None,
        "e": {"f": {"g": None}}
    }
    expected = {
        "a": {"c": 1}
    }
    assert sd._remove_null(input_dict) == expected

    # Empty dict
    assert sd._remove_null({}) == {}

    # Dict with empty dict
    assert sd._remove_null({"a": {}}) == {}


def test_remove_null_lists():
    """Test _remove_null with lists"""
    sd = StringifyDict()
    # Simple list
    assert sd._remove_null([1, None, 2, None]) == [1, 2]

    # Nested list
    assert sd._remove_null([
        [1, None],
        None,
        [None, 2]
    ]) == [[1], [2]]

    # List with dicts
    assert sd._remove_null([
        {"a": 1, "b": None},
        None,
        {"c": None}
    ]) == [{"a": 1}]

    # Empty list
    assert sd._remove_null([]) == []

    # List with all nulls
    assert sd._remove_null([None, None]) == []


def test_complex_nested_structures():
    """Test with complex nested structures"""
    sd = StringifyDict()
    input_data = {
        "list_of_dicts": [
            {"a": 1, "b": None},
            None,
            {"c": {"d": None}}
        ],
        "dict_of_lists": {
            "l1": [1, None, 2],
            "l2": None,
            "l3": [None, {"x": None, "y": 1}]
        }
    }
    expected = {
        "list_of_dicts": [
            {"a": 1}
        ],
        "dict_of_lists": {
            "l1": [1, 2],
            "l3": [{"y": 1}]
        }
    }
    assert sd._remove_null(input_data) == expected


def test_edge_cases():
    """Test edge cases"""
    sd = StringifyDict()
    # Non-dict/list input for remove_null
    assert sd._remove_null("string") == "string"
    assert sd._remove_null(123) == 123

    # Special numeric values
    assert sd._prepare_value(float('inf')) == "inf"
    assert sd._prepare_value(float('-inf')) == "-inf"

    # Empty structures
    assert sd._remove_null([{}]) == []
    assert sd._remove_null({"a": []}) == {"a": []}


def test_class_instantiation():
    """Test class instantiation and dict inheritance"""
    # Empty initialization
    sd1 = StringifyDict()
    assert isinstance(sd1, dict)
    assert len(sd1) == 0

    # Initialize with data
    data = {"a": 1, "b": None}
    sd2 = StringifyDict(data)
    assert isinstance(sd2, dict)
    assert sd2 == data


@pytest.mark.parametrize("input_data,expected", [
    (
            {"a": 1, "b": None},
            {"a": "1"}
    ),
    (
            {"list": [1, None, {"a": None, "b": 2}]},
            {"list": ["1", {"b": "2"}]}
    ),
    (
            {"dict": {"a": None, "b": [1, None]}},
            {"dict": {"b": ["1"]}}
    ),
    (
            {"mixed": [{"a": None}, None, {"b": 1}]},
            {"mixed": [{"b": "1"}]}
    ),
])
def test_combined_operations(input_data, expected):
    """Test combining _remove_null and _prepare_value operations"""
    sd = StringifyDict()
    cleaned = sd._remove_null(input_data)
    prepared = sd._prepare_value(cleaned)
    assert prepared == expected


def test_preserve_original_data():
    """Test that original data is not modified"""
    original_data = {
        "a": [1, None, 2],
        "b": {"c": None, "d": 3}
    }
    sd = StringifyDict(original_data.copy())

    # Perform operations
    cleaned = sd._remove_null(dict(sd))
    prepared = sd._prepare_value(cleaned)

    # Check original data is unchanged
    assert sd == original_data