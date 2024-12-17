from asset_core.objects.object_source import ObjectSource


def test_init(mock_gcs_blob):
    obj_source = ObjectSource(blob=mock_gcs_blob, path="test/file_1.jpg")
    assert obj_source.blob == mock_gcs_blob
    assert obj_source.path_in_asset == "test/file_1.jpg"
    assert obj_source.callback is None
