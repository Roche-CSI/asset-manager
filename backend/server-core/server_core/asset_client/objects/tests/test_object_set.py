import fnmatch
import os
from src.asset.objects import Object


def test_get_element(asset):
    first = asset.linked_objects.element(0)
    assert isinstance(first, Object)
    assert first == asset.linked_objects.first


def test_filter(asset):
    extensions = [".txt", ".jpg"]
    for ext in extensions:
        selected = asset.linked_objects.filter(predicate=lambda x: fnmatch.fnmatchcase(x.path, "*" + ext))
        assert len(selected) > 0
        for obj in selected:
            path, ext = os.path.splitext(obj.path)
            assert ext == ext

