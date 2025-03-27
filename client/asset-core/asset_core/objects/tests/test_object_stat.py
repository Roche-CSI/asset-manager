from asset_core.objects.object_stat import ObjectStat


def test_serialize_fields():
    expected_fields = [
        "id",
        "content_time",
        "metadata_time",
        "num_links",
        "inode",
        "size",
        "linked"
    ]
    assert ObjectStat.serialize_fields() == expected_fields
