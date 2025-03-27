from asset_core.objects.group.group_object import GroupObject
from asset_core.objects.object_factory import ObjectFactory


def test_bulk_create(asset, test_data):
    object_factory = ObjectFactory()
    sources = object_factory.parse_sources(repo_dir=asset.repo_dir, targets=[test_data])
    sources = [src for src in sources['posix']]
    for i in range(len(sources)):
        sources[i].content = asset.contents.items[i]

    objects = GroupObject.bulk_create(factory=object_factory, sources=sources, repo_dir=asset.repo_dir)
    assert len(objects) == 1
    assert len(objects[0].members) == 2
    assert objects[0].object_type == "group"
    assert objects[0].has_raw_mode is True
    assert objects[0].path == '.asset/.raw/4db7ec901044b2e864ab3499647654ca.zip'


def test_serialize_fields():
    expected_fields = ['id', 'url_id', 'created_by', 'created_at', 'object_type', 'content', 'object_type']
    assert GroupObject.serialize_fields() == expected_fields
