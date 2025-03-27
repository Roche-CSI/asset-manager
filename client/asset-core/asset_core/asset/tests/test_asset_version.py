import pytest

from asset_core.asset.asset_version import AssetVersion
from asset_utils.common import exceptions


def test_parse_name():
    data = {
        "asset_name": exceptions.InvalidAssetNameError,
        "asset_name/1": ("asset_name", "1", None, None, None),
        "asset_name/1/0.0.1": ("asset_name", "1", "0.0.1", None, None),
        "asset_name/1/temp_1": exceptions.InvalidVersionError,
        "asset_name/1/0.0.1/temp_1": ("asset_name", "1", "0.0.1", None, "temp_1"),
        "asset_name/temp_id": ("asset_name", "temp_id", None, None, None),
        "asset_name/temp_id/0.0.1": ("asset_name", "temp_id", "0.0.1", None, None),
        "asset_name/alias/0.0.1": ("asset_name", None, "0.0.1", "alias", None),
        "asset_name/alias/0.0.1/temp_1": ("asset_name", None, "0.0.1", "alias", "temp_1"),
        "asset_name/alias/0.0.1/dir/child/file.txt": ("asset_name", None, "0.0.1", "alias", "dir/child/file.txt"),
        "asset_name/alias/0.0.1/dir/child/grandchild/": ("asset_name", None, "0.0.1", "alias", "dir/child/grandchild/"),
    }

    for asset_handle in data:
        expected = data[asset_handle]
        if isinstance(expected, tuple):
            result: dict = AssetVersion.parse_name(asset_handle, default_to_root=False)
            assert result.get("class_name") == expected[0]
            assert result.get("seq_id") == expected[1]
            assert result.get("version") == expected[2]
            assert result.get("alias") == expected[3]
            assert result.get("extras") == expected[4]

        else:
            with pytest.raises(expected_exception=expected):
                AssetVersion.parse_name(asset_handle)
