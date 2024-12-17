from asset_core.asset.refs import AssetRef


def test_create(empty_asset):
    test_data = [
        {
            "src_ver_name": "acm_images/1/0.0.0",
            "src_ver_id": 4,  # wrong data but if its local ref should be created since we are passing id
            "dst_ver_id": 6,
            "dst_ver_name": "test_asset/1/0.0.0",
            "label": "validation",
            "properties": None,
            "remote": False
        },
        {
            "src_ver_name": "acm_images/1/0.0.0",
            "src_ver_id": 3,
            "dst_ver_id": 8,
            "dst_ver_name": "test_asset/1/0.0.0",
            "label": "validation",
            "properties": None,
            "remote": False
        }
    ]
    for data in test_data:
        ref = AssetRef.create(**data, **{"asset": empty_asset})
        assert ref.src_version.get("id") == data["src_ver_id"]
        assert ref.dst_version.get("id") == data["dst_ver_id"]


def test_serialize(empty_asset):
    test_data = [
        {
            "dst_ver_id": 45,
            "src_ver_id": 21,
            "src_ver_name": "dl_training/45/0.0.1",
            "dst_ver_name": "ml_data/1/0.1.1",
            "label": "random"
        },
        {
            "dst_ver_id": 93,
            "src_ver_id": 54,
            "src_ver_name": "ml_models/21/1.0.2",
            "dst_ver_name": "ml_data/1/0.1.1",
            "label": "random"
        },
        {
            "dst_ver_id": 93,
            "src_ver_id": 23,
            "src_ver_name": "ml_models/21/1.0.2",
            "dst_ver_name": "ml_data/1/0.1.1",
            "label": "random"
        }
    ]
    for data in test_data:
        ref = AssetRef.create(asset=empty_asset, **data)
        serialized = ref.serialize()
        # id gets assigned by server, so test should have id as None
        assert serialized.get("id") is None
        assert serialized["label"] == data["label"]
        assert serialized["src_version"]["id"] == data["src_ver_id"]
        assert serialized["src_version"]["name"] == data["src_ver_name"]
        assert serialized["dst_version"]["id"] == data["dst_ver_id"]
        assert serialized["dst_version"]["name"] == data["dst_ver_name"]


def test_deserialize(empty_asset):
    test_data = [
        {
            "src_version": {"id": 21, "name": "dl_training/45/0.0.1"},
            "dst_version": {"id": 45, "name": "ml_data/1/0.1.1"},
            "label": "random"
        },
        {
            "src_version": {"id": 93, "name": "ml_data/21/1.0.2"},
            "dst_version": {"id": 54, "name": "ml_models/1/0.1.1"},
            "label": "random"
        }
    ]
    for data in test_data:
        ref = AssetRef.de_serialize(asset=empty_asset, data=data)
        for key in data:
            assert getattr(ref, key)
        expected_repr = f'{data["src_version"]["name"]}<->{data["dst_version"]["name"]}'
        assert ref.unique_repr == expected_repr
