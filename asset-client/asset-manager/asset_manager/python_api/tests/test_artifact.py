import pytest

from asset_manager.python_api.artifact import Artifact, File
from asset_utils.common import exceptions


@pytest.fixture(scope='module')
def asset_path():
    return "/Users/mahantis/am_demo/acap_e2e_assets/1"


def test_fixtures(asset_root, repo, asset, store, empty_asset):
    print(asset_root)
    print(repo)
    print(asset)
    print(store)
    print(empty_asset)

    artifact = Artifact(path=repo.fs_path)
    info = artifact.info
    print(info)


def test_init():
    # Should raise exception if path is missing or None
    with pytest.raises(Exception) as e:
        Artifact(path=None)
    assert e.type == exceptions.AssetException

    # also raise exception if not a valid repo
    with pytest.raises(Exception) as e:
        Artifact(path="/Users/mahantis")
    assert e.type == exceptions.NotAssetRepoError


def test_info(asset):
    artifact = Artifact(path=asset.repo.fs_path)
    expected = ["asset", "objects"]
    for key in expected:
        assert key in artifact.info

    # objects
    object_keys = ["linked_path", "path", "size", "cloned"]
    for item in artifact.info.get("objects"):
        for key in object_keys:
            assert key in item


def test_versions(asset):
    artifact = Artifact(path=asset.repo.fs_path)
    versions = artifact.versions
    assert versions is None  # local asset


def test_history(asset_path, asset):
    artifact = Artifact(path=str(asset.repo))
    versions = artifact.history
    print(versions)


def test_status(asset):
    # path = "/Users/mahantis/am_demo/dsaswe_test/24"
    artifact = Artifact(path=str(asset.repo))
    status = artifact.status
    print(status)


def test_files(asset):
    # path = "/Users/mahantis/am_demo/dsaswe_test/24"
    artifact = Artifact(path=str(asset.repo))
    files = artifact.files
    print(files)


def test_read_file():
    path = "/Users/mahantis/am_demo/dsaswe_test/24"
    artifact = Artifact(path=path)
    file: File = artifact.files.get("info-test.txt")
    with file.open() as f:
        contents = f.read()
        print(contents)


def test_find_alias():
    # find with alias
    asset_name = Artifact.find(class_name="swarup_data", alias="group_object_proxy_test")
    assert asset_name == "swarup_data/8"


def test_find_hash():
    # find with hash
    asset_names = Artifact.find(class_name="swarup_data", hash="12adc50b32d57b3d17cc829e4cd02c2b")
    assert asset_names and asset_names[0] == "swarup_data/1/0.0.0"


def test_clone():
    artifact = Artifact.clone(name="swarup_data/1", path="/Users/mahantis/am_demo/swarup_data/1")
    print(artifact)


def test_sort_key():
    asset_names = ["swarup_data/3/2.1.9", "swarup_data/3/2.10.0", "swarup_data/1/10.0.2"]

    def sort_key(name):
        # Split the string by '/' and extract parts
        parts = name.split('/')
        return parts[0], int(parts[1]), tuple(map(int, parts[2].split(".")))

    asset_names.sort(key=sort_key)
    assert asset_names[-1] == "swarup_data/3/2.10.0"
