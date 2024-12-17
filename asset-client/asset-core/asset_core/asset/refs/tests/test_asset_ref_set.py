from asset_core.asset.refs import AssetRef


def test_data():
    return [
        {
            "src_version": {"id": 21, "name": "dl_training/45/0.0.1"},
            "dst_version": {"id": 45, "name": "ml_data/1/0.1.1"},
            "label": "random"
        },
        {
            "src_version": {"id": 93, "name": "ml_models/21/1.0.2"},
            "dst_version": {"id": 54, "name": "ml_data/1/0.1.1"},
            "label": "random"
        }
    ]


def ref_objects(asset):
    asset = asset
    return [AssetRef.de_serialize(asset=asset, data=data) for data in test_data()]


def test_add(empty_asset):
    asset = empty_asset
    refs = ref_objects(asset=empty_asset)
    asset.refs.add_refs(refs=refs)
    # verify it got added
    for ref in refs:
        assert ref in asset.refs


def test_find(empty_asset):
    asset = empty_asset
    refs = ref_objects(asset=empty_asset)
    asset.refs.add_refs(refs)
    found = asset.refs.find(asset_names=[refs[0].src_version["name"]])
    assert found[0].serialize() == refs[0].serialize()


def test_deserialize(empty_asset):
    asset = empty_asset
    asset.refs.de_serialize(data=test_data())
    assert len(asset.refs) == len(test_data())
    for data in test_data():
        ref = AssetRef.de_serialize(asset=asset, data=data)
        assert ref in asset.refs


def test_serialize(empty_asset):
    asset = empty_asset
    data = test_data()
    asset.refs.de_serialize(data=data)
    serialized = asset.refs.serialize()
    extras = ["id", "created_by", "created_at", "properties"]
    for idx, ref_data in enumerate(serialized):
        for field in extras:
            assert field in ref_data
        expected = data[idx]
        for key in expected:
            assert expected[key] == ref_data[key]
