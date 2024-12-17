import pytest

from asset_core.asset.asset_handle import AssetHandle


def test_is_temp(store):
    data = {
        "dsaswe_test/2/0.0.1": False,
        "dsaswe_test/temp_12345": True,
        "dsaswe_test/alias_1": False,
    }
    for name, expected in data.items():
        handle = AssetHandle.from_name(asset_name=name)
        assert handle.is_temp() == expected


def test_from_name(store):
    asset_names = {
        "dsaswe_test/2/0.0.1": AssetHandle(class_name="dsaswe_test",
                                           seq_id="2",
                                           version="0.0.1"),
        "dsaswe_test/2": AssetHandle(class_name="dsaswe_test",
                                     seq_id="2"),
        "dsaswe_test": "error",
        "dsaswe_test/alias_1": AssetHandle(class_name="dsaswe_test",
                                           alias="alias_1"),
        "dsaswe_test/alias_2/0.0.2/sample_files/demo.txt": AssetHandle(class_name="dsaswe_test",
                                                                       alias="alias_2",
                                                                       version="0.0.2",
                                                                       extras="sample_files/demo.txt")
    }
    for name, expected in asset_names.items():
        if expected == "error":
            with pytest.raises(Exception) as e:
                AssetHandle.from_name(asset_name=name)
                assert e
        else:
            handle = AssetHandle.from_name(asset_name=name)
            assert handle.class_name == expected.class_name
            assert handle.seq_id == expected.seq_id
            assert handle.version == expected.version
            assert handle.alias == expected.alias
            assert handle.extras == expected.extras
