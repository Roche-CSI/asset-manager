import os

import pytest

from asset_core.store import AssetStore


def test_remote_storage(store):
    assert os.getenv("ASSET_STAGING_URL") == "gs://test_bucket/assets/staging"
    assert os.getenv("ASSET_REMOTE_URL") == "gs://test_bucket/assets/remote"


def test_store_properties(store):
    # store is set to ASSET_HOME
    assert store.home_dir == os.environ.get("ASSET_HOME")
    # .assets is created
    assert str(store.store_dir).endswith(".assets") and os.path.exists(store.store_dir)
    # store.yaml
    assert os.path.relpath(store.store_file, store.store_dir) == "store.json"
    # project_id is not None
    assert store.project_id
    # store_id is accurate
    assert os.path.exists(store.store_identifier)
    assert str(os.path.relpath(store.store_identifier, store.store_dir)).startswith(".")
    # assets are stored inside project dir
    assert str(os.path.relpath(store.project_dir, store.store_dir)) == store.project_id
    # asset cache is also inside projects
    assert os.path.relpath(store.assets_cache_dir, store.store_dir) == f"{store.project_id}/assets"
    # asset class cache
    assert os.path.relpath(store.asset_classes_dir, store.store_dir) == f"{store.project_id}/asset_classes"
    # content cache is inside project
    assert os.path.relpath(store.contents_cache_dir(class_id="test_class"),
                           store.store_dir) == f"{store.project_id}/contents/test_class"
    # manifests backup is also inside the project
    assert os.path.relpath(store.manifests_dir, store.store_dir) == f"{store.project_id}/manifests"


def test_is_store_exists(store):
    assert AssetStore.is_store_exists(dir_path=store.home_dir)

    # invalid path - should raise exception
    with pytest.raises(Exception) as e:
        assert AssetStore.is_store_exists("/not-existing/path")
    assert e

    # valid path but invalid store
    assert AssetStore.is_store_exists(os.path.dirname(store.home_dir)) is False


def test_get_store_dir(store):
    dir_path = AssetStore.get_store_dir(store.home_dir)  # without .assets
    assert dir_path == store.store_dir

    dir_path = AssetStore.get_store_dir(store.store_dir)  # with .assets
    assert dir_path == store.store_dir
