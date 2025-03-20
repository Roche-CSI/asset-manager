import pytest

from asset_utils.common.better_set import BetterSet


def test_initialization():
    # Test initialization with no items
    empty_set = BetterSet()
    assert len(empty_set) == 0

    # Test initialization with one item
    single_item_set = BetterSet("item1")
    assert "item1" in single_item_set

    # Test initialization with multiple items
    multi_item_set = BetterSet("item1", "item2")
    assert len(multi_item_set) == 2
    assert "item1" in multi_item_set and "item2" in multi_item_set


def test_add_extend():
    test_set = BetterSet()
    test_set.add("item1")
    assert "item1" in test_set
    # Test extend with a duplicate item
    test_set.extend(["item1", "item2"])
    assert "item1" in test_set and "item2" in test_set
    assert len(test_set) == 2


def test_remove_discard():
    test_set = BetterSet("item1", "item2")
    test_set.remove("item1")
    assert "item1" not in test_set
    # Test discard does not raise an error if item does not exist
    test_set.discard("item3")
    assert "item3" not in test_set
    # Test remove raises KeyError if item does not exist
    with pytest.raises(KeyError):
        test_set.remove("item3")


def test_contains_get():
    test_set = BetterSet("item1")
    assert test_set.contains("item1")
    assert not test_set.contains("item2")

    assert test_set.get("item1") == "item1"
    assert test_set.get("item2") is None


def test_clear():
    test_set = BetterSet("item1", "item2")
    test_set.clear()
    assert len(test_set) == 0


def test_union():
    set1 = BetterSet("item1", "item2")
    set2 = BetterSet("item2", "item3")
    union_set = set1.union(set2)
    assert len(union_set) == 3
    assert "item1" in union_set and "item2" in union_set and "item3" in union_set
