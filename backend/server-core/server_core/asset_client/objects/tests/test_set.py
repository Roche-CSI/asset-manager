from src.utils.better_set import BetterSet
import pytest


@pytest.fixture(scope="module")
def test_set():
    return BetterSet(*[1, 2, 3, 4, 5])


def test_create(test_set):
    for item in [1, 2, 3, 4, 5]:
        assert item in test_set


def test_iterate(test_set):
    for item in test_set:
        assert item in [1, 2, 3, 4, 5]


def test_length(test_set):
    assert len(test_set) == 5


def test_union(test_set):
    d = BetterSet(5, 7, 8)
    result = test_set.union(d)
    for item in [1, 2, 3, 4, 5, 7, 8]:
        assert item in result
    assert len(result) == 7
    assert result.first == 1
    assert result.last == 8


def test_cast_to_list(test_set):
    assert list(test_set) == [1, 2, 3, 4, 5]
