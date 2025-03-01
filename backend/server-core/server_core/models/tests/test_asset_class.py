from server_core.models.asset_class import AssetClass
from server_core.models.utils import delete_records
from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from server_core.gcp.sync_gcp import get_blob_from_url, get_blob_contents
from server_core.configs import Configs
import pytest
import yaml


@pytest.fixture(scope="module")
def classes_data(test_app):
    """need the test_app fixture for making db transactions"""
    return [
        "genetics",
        "gene_data",
        "dl_training",
        "bio_nlp",
        "ac_modeling",
        "imaging"
    ]


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "assetclass" in tables


def test_crud_operations(test_user, test_project):
    # need the test_app fixture for db operations

    # create
    asset_cls = AssetClass.get_or_create(user=test_user, name="gene_data", project=test_project)[0]
    assert asset_cls.owner == test_user
    assert asset_cls.created_by == test_user
    assert asset_cls.name == "gene_data"

    # update and read
    asset_cls.name = "gene_data2"
    asset_cls.save(user=test_user)
    saved: AssetClass = AssetClass.get_if_exists(AssetClass.id == asset_cls.id)
    assert saved.name == "gene_data2"

    # soft delete
    saved.delete_instance(user=test_user)
    soft_del: AssetClass = AssetClass.get_if_exists(
        AssetClass.id == saved.id,
        include_deleted_records=True
    )
    assert soft_del.status == soft_del.statuses.DELETED

    # soft delete records shouldn't be publicly accessible
    public = AssetClass.get_if_exists(AssetClass.id == saved.id)
    assert public is None

    # permanent delete
    saved.delete_instance(user=test_user, permanently=True)
    exists = AssetClass.get_if_exists(
        AssetClass.id == saved.id,
        include_deleted_records=True
    )
    assert exists is None


def test_write_classes_yaml(test_user, classes_data, test_project):
    records = []
    for name in classes_data:
        asset_cls: AssetClass = AssetClass.create(user=test_user.username, name=name, project=test_project)
        class_url, class_list_url = asset_cls.write_to_bucket()
        # fetch and test
        storage = StorageFactory.storage_for_url(src_url=class_url)
        class_blob = storage.get_blob(url_string=class_url)
        assert class_blob and class_blob.size > 0
        class_list_blob = storage.get_blob(url_string=class_list_url)
        assert class_list_blob and class_list_blob.size > 0

        # contents = get_blob_contents(blob)
        # data: dict = yaml.load(contents)
        # serialized = asset_cls.to_dict(fields=AssetClass.yaml_fields())
        # for field in AssetClass.yaml_fields():
        #     assert serialized.get(field) == data.get(field)
        records.append(
            asset_cls
        )

    # clean up
    delete_records(records, AssetClass, test_user)


