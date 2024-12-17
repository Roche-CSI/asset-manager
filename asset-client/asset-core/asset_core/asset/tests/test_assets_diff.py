# from src.asset.asset_diff import AssetDiff
# from src.utils.file_utils import FileUtils
# import os
#
#
# def test_files():
#     dir_name = os.path.dirname(__file__)
#     return os.path.join(dir_name, "manifest1.yaml"), os.path.join(dir_name, "manifest2.yaml")
#
#
# def test_assets_delta():
#     manifest1, manifest2 = test_files()
#     manifest1 = FileUtils.read_yaml(manifest1)
#     manifest2 = FileUtils.read_yaml(manifest2)
#     patch: str = compute_assets_patch(prev_assets=manifest1["assets"], curr_assets=manifest2["assets"])
#     assert patch is not None
#     # apply patch and check again
#     result = apply_assets_patch(prev_assets=manifest1["assets"], patch=patch)
#     assert result == manifest2["assets"]
#
#
# def test_assets_delta2():
#     dir_name = os.path.dirname(__file__)
#     m1, m2 = os.path.join(dir_name, "manifest1.1.yaml"), os.path.join(dir_name, "manifest2.1.yaml")
#     m1 = FileUtils.read_yaml(m1)
#     m2 = FileUtils.read_yaml(m2)
#     patch: str = compute_assets_patch(prev_assets=m1["objects"], curr_assets=m2["objects"])
#     assert patch is not None
#     # apply patch and check again
#     result = apply_assets_patch(prev_assets=m1["objects"], patch=patch)
#     assert result == m2["objects"]
