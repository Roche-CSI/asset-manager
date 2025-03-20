import fnmatch
import os
from asset_core.objects import Object


def test_get_element(asset):
    first = asset.objects.first
    assert isinstance(first, Object)
    assert first == asset.objects[0]


def test_filter(asset):
    extensions = [".jpg"]
    for ext in extensions:
        selected = asset.objects.filter(predicate=lambda x: fnmatch.fnmatchcase(x.path, "*" + ext))
        assert len(selected) > 0
        for obj in selected:
            path, ext = os.path.splitext(obj.path)
            assert ext == ext


def test_find(asset):
    paths = [asset.objects.first.linked_path]
    found = asset.objects.find(paths)
    assert len(found) == 1
