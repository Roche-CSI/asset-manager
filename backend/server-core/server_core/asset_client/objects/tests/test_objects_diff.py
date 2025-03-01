import os
from utils.file_utils import FileUtils
from asset_client.asset import Asset
from asset_client.objects.objects_diff import ObjectsDiff


def assets_data():
    """need the test_app fixture for making db transactions"""
    path = os.path.join(os.path.dirname(__file__), "test_data.json")
    path2 = os.path.join(os.path.dirname(__file__), "test_data2.json")
    return FileUtils.read_json(path), FileUtils.read_json(path2)


def test_compute_dict_patch(test_user, test_app):
    data1, data2 = assets_data()
    asset1 = Asset(user=test_user, data=data1)
    asset2 = Asset(user=test_user, data=data2)
    # diff = compute_dict_patch(asset1.objects.serialize(), asset2.objects.serialize())
    removed = ['gs:md5$placeholder_id_001==::example_data/.DS_Store',
               'gs:md5$placeholder_id_002==::example_data/file2.txt"']

    ddiff = ObjectsDiff()
    ddiff.compute_diff(from_objects=asset1.objects, to_objects=asset2.objects)
    assert ddiff.removed == removed

    # remove one extra object from asset1 and add to asset2 and check again
    added = None
    for object in asset1.objects:
        if object.id not in removed:
            asset1.objects.remove_objects([object])
            asset2.objects.add_objects([object])
            added = object.id
            break

    ddiff.compute_diff(from_objects=asset1.objects, to_objects=asset2.objects)
    assert ddiff.removed == removed
    assert ddiff.added == [added]

    # add the removed objects and check again
    for object in asset1.objects:
        if object.id in removed:
            asset2.objects.add_objects([object])

    ddiff.compute_diff(from_objects=asset1.objects, to_objects=asset2.objects)
    assert ddiff.removed == []
    assert ddiff.added == [added]



