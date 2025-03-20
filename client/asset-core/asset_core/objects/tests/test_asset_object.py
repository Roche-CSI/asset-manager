import pytest

from asset_contents import Content
from asset_core.objects.asset_object import AssetObject
from asset_core.objects.object_factory import ObjectFactory
from asset_core.objects.object_source import ObjectSource


@pytest.fixture
def content():
    return Content(id="content_id", mime_type="text/plain")


def test_create(content):
    obj = AssetObject.create(content=content, path="test/path")
    assert obj.id == "content_id::test/path"
    assert obj.content == content
    assert obj.path == "test/path"


def test_bulk_create(mock_gcs_blob, content):
    source = ObjectSource(blob=mock_gcs_blob, path="test/file_1.jpg")
    source.content = content
    objects = AssetObject.bulk_create(factory=ObjectFactory(), sources=[source])
    assert len(objects) == 1
    assert objects[0].id == "content_id::test/file_1.jpg"
    assert objects[0].content == content
    assert objects[0].path == "test/file_1.jpg"
