import os

from asset_core.objects import Object
from asset_utils.utils.file_utils import FileUtils


def test_file_delete(asset):
    # asset fixture
    obj: Object = asset.objects.first
    # delete file and check
    os.unlink(obj.linked_path)
    assert os.path.exists(obj.linked_path) is False
    assert obj.edit_status() == obj.edit_statuses.DELETED
    # re-add and check again
    obj.link_from_store()
    assert os.path.exists(obj.linked_path)
    assert obj.edit_status() == obj.edit_statuses.UNCHANGED


def test_file_rename(asset):
    # rename and check
    obj = asset.objects.items[0]
    path, ext = os.path.splitext(obj.linked_path)
    new_ext = ext + "_temp"
    os.rename(src=obj.linked_path, dst=path + new_ext)
    assert obj.edit_status() == obj.edit_statuses.DELETED
    # restore and check again
    os.rename(src=path + new_ext, dst=obj.linked_path)
    assert obj.edit_status() == obj.edit_statuses.UNCHANGED


def test_file_changed(asset):
    # modify content and check
    object1, object2 = asset.objects[0], asset.objects[1]
    # cross link
    FileUtils.copy_file(object1.linked_path, object2.linked_path)
    assert object2.edit_status() == object2.edit_statuses.MODIFIED
