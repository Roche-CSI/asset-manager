import json

from asset_core.api.repo_api.union import UnionApi


def test_union_id(empty_asset):
    api = UnionApi(asset=empty_asset)
    union_hash = api.get_union_hash(asset_id=empty_asset.id, src_ver="0.0.0", dst_ver="0.0.50")
    print(f"combine_hash: {union_hash}")
    parsed = api.parse_union_hash(hash_string=union_hash)
    print(f"parsed: {json.dumps(parsed)}")
