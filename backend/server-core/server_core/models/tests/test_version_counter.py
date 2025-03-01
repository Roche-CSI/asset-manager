import pytest
from server_core.models.version_counter import VersionCounter
from server_core.models.asset_version import AssetVersion
from server_core.models.asset_class import AssetClass
from server_core.models.asset import Asset
from server_core.models.utils import delete_records
import uuid


@pytest.fixture(scope="module")
def asset_record(test_user, test_app):
    # test_app fixture required for db transactions
    asset_class_record = AssetClass.get_if_exists(AssetClass.name == "gene_data") or \
                         AssetClass.create(user=test_user, name="gene_data")

    asset_record = Asset.create(user=test_user, asset_class=asset_class_record)
    yield asset_record
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records([asset_record], Asset, test_user)
    delete_records([asset_class_record], AssetClass, test_user)


def get_objects_data():
    return [
        [
            "gs:md5$placeholder_id_001==::example_data/.DS_Store",
            "gs:md5$placeholder_id_002==::example_data/file2.txt"
        ],
        [
            "gs:md5$placeholder_id_004==::example_data/img2.jpg",
            "gs:md5$placeholder_id_005==::example_data/img3.jpg",
        ],
        [
            "gs:md5$placeholder_id_006==::example_data/img4.jpg",
            "gs:md5$placeholder_id_007==::example_data/img5.jpg",
            "gs:md5$placeholder_id_008==::example_data/img6.jpg",
        ],
        [
            "gs:md5$placeholder_id_003==::example_data/img1.jpg",
            "gs:md5$placeholder_id_009==::example_data/img7.jpg"
        ]
    ]


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "versioncounter" in tables


def test_crud_operations(asset_record, test_user):
    objects_data = get_objects_data()
    version_records = []
    for data in objects_data:
        version_record: AssetVersion = AssetVersion.create(user=test_user,
                                                           asset=asset_record,
                                                           objects=data,
                                                           commit_hash=uuid.uuid4().hex.encode("ascii")
                                                           )
        version_records.append(version_record)

    leaf_version = version_records[len(version_records) - 1]
    counter: VersionCounter = asset_record.version_counter.get()
    assert counter.leaf_version == leaf_version
    assert counter.leaf_objects == objects_data[len(objects_data) - 1]

    # reverse the list to avoid foreign-key constraints in deletion
    delete_records(list(reversed(version_records)), AssetVersion, test_user)

