import pytest
import uuid
import os
from server_core.asset_client.asset import Asset
from server_core.models.asset import Asset as AssetModel
from server_core.models.asset_class import AssetClass
from server_core.models.asset_version import AssetVersion
from server_core.models.version_counter import VersionCounter
from server_core.models.utils import delete_records
from server_core.utils.file_utils import FileUtils


@pytest.fixture(scope="module")
def asset(test_app, test_user):
    """need the test_app fixture for making db transactions"""
    path = os.path.join(os.path.dirname(__file__), "test_data.json")
    asset = Asset(user=test_user, data=FileUtils.read_json(path))
    yield asset


@pytest.fixture(scope="module")
def asset_record(test_user, test_app, test_project, asset) -> AssetModel:
    # test_app fixture required for db transactions
    asset_class_record = AssetClass.get_if_exists(AssetClass.name == asset.asset_class.name)
    if not asset_class_record:
        asset_class_record = AssetClass.create(user=test_user, name=asset.asset_class.name, project=test_project)

    asset_record = AssetModel.create(user=test_user, asset_class=asset_class_record)
    asset.asset_class.id = str(asset_class_record.id)
    yield asset_record
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records(asset_record, AssetModel, test_user)
    delete_records(asset_class_record, AssetClass, test_user)


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "assetversion" in tables


def test_crud_operations(test_user, asset_record, asset: Asset):
    # create without objects, should raise exception
    with pytest.raises(Exception) as e:
        version_record = AssetVersion.create(user=test_user, asset=asset_record)
    assert str(e.value) == "version can not be created without any objects to commit"

    version_record: AssetVersion = AssetVersion.create(user=test_user,
                                                       asset=asset_record,
                                                       objects=asset.objects,
                                                       commit_hash=asset.objects.hash
                                                       )
    assert version_record and isinstance(version_record, AssetVersion)
    assert version_record.number == "0.0.0"
    # assert sorted(version_record.patch["added"]) == sorted(objects_data[1])
    assert version_record.commit_hash

    # list
    all_versions = AssetVersion.select().where(AssetVersion.id == version_record.id)
    assert len(all_versions) == 1

    # list using foreign key
    versions = asset_record.versions
    for version in versions:
        assert version.id == version_record.id

    # try to update, should throw error
    with pytest.raises(Exception) as e:
        version_record.number = "0.2.2"
        version_record.save(user=test_user)
    assert str(e.value) == AssetVersion.read_only_error()

    # soft delete
    version_record.delete_instance(user=test_user)
    deleted = AssetVersion.get_if_exists(
        AssetVersion.id == version_record.id, include_deleted_records=True)
    assert deleted.id == version_record.id
    assert deleted.status == deleted.statuses.DELETED
    assert deleted.soft_delete_by == test_user

    # public should be None
    public = AssetVersion.get_if_exists(AssetVersion.id == version_record.id)
    assert public is None

    # permanent delete
    deleted.delete_instance(user=test_user, permanently=True)
    exists = AssetVersion.get_if_exists(AssetVersion.id == version_record.id, include_deleted_records=True)
    assert exists is None


def create_version_records(asset_record, objects_data, non_committed, user):
    # test with non-committed versions
    records = set()
    for idx, data in enumerate(objects_data):
        # leave one one last so we can test commit_hash query also
        commit_hash = uuid.uuid4().hex.encode("ascii") if idx <= len(objects_data) - (non_committed + 1) else None
        records.add(
            AssetVersion.create(user=user,
                                asset=asset_record,
                                objects=data,
                                commit_hash=commit_hash
                                )
        )
    return records

def test_compute_patch(asset_record, test_user, asset):
    """should be calculated added and removed correctly"""
    version: AssetVersion = AssetVersion.create(user=test_user,
                                                asset=asset_record,
                                                commit_hash=uuid.uuid4().hex.encode("ascii"),
                                                objects=asset.objects)
    assert compare_patches(version.patch,
                           AssetVersion.compute_diff(from_objects=[],
                                                     to_objects=[object.id for object in asset.objects]
                                                     ))
    # since all items in object_data are unique, the current item should show up as added
    # previous should show up as removed
    expected = sorted([object.id for object in asset.objects])
    assert sorted(version.patch["added"]) == expected
    assert sorted(version.patch["removed"]) == []
    # verify leaf objects
    leaf_objects = sorted(asset_record.version_counter.get().leaf_objects)
    assert leaf_objects == expected
    # cleanup
    delete_records(version, AssetVersion, test_user)


def test_find(asset_record, test_user, asset):
    version: AssetVersion = AssetVersion.create(user=test_user,
                                                asset=asset_record,
                                                commit_hash=asset.objects.hash,
                                                objects=asset.objects.serialize())

    name = f"{asset_record.asset_class.name}/{asset_record.seq_id}/{version.number}"
    found = AssetVersion.find(project_id=asset_record.asset_class.project_id, name=name)
    assert found.id == version.id
    delete_records(version, AssetVersion, test_user)


def test_find_with_hash(asset_record, test_user, asset):
    version: AssetVersion = AssetVersion.create(user=test_user,
                                                asset=asset_record,
                                                commit_hash=asset.objects.hash,
                                                objects=asset.objects)

    # check with class_name
    found = list(AssetVersion.find_with_hash(class_name=asset_record.asset_class.name, commit_hash=version.commit_hash))
    assert len(found) == 1 and found[0].id == version.id

    # without class_name
    found = list(AssetVersion.find_with_hash(commit_hash=version.commit_hash))
    assert len(found) == 1 and found[0].id == version.id

    # test exception
    with pytest.raises(Exception) as e:
        found = list(AssetVersion.find_with_hash(class_name=asset_record.asset_class.name, commit_hash=None))
    assert e and str(e.value) == "hash can not be null"

    delete_records(version, AssetVersion, test_user)


def compare_patches(patch1, patch2):
    for key in patch1:
        if sorted(patch1[key]) != sorted(patch2[key]):
            return False
    return True
