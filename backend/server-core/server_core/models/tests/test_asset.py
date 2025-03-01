import pytest
from peewee import DoesNotExist

from server_core.models.asset import Asset
from server_core.models.asset_class import AssetClass


@pytest.fixture(scope="module")
def asset_class(test_user, test_project):
    # test_app fixture required for db transactions
    try:
        asset_cls = AssetClass.get(AssetClass.name == "gene_data",
                                   AssetClass.project == test_project)
    except DoesNotExist as e:
        asset_cls = AssetClass.create(user=test_user,
                                      name="gene_data",
                                      project=test_project,
                                      id="2d7133cd-1072-4a96-b14b-62c67b6a214f"
                                      )
    yield asset_cls
    asset_cls.delete_instance(user=test_user, permanently=True)
    assert AssetClass.get_if_exists(AssetClass.id == asset_cls.id, include_deleted_records=True) is None


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "asset" in tables


def test_crud_operations(test_user, asset_class: AssetClass):
    # create
    asset: Asset = Asset.create(user=test_user, asset_class=asset_class)
    assert asset.owner == asset.created_by == test_user
    assert asset.seq_id == asset_class.counter
    assert asset.asset_class == asset_class

    # list
    all_assets = Asset.select().where(Asset.id == asset.id)
    assert len(all_assets) == 1

    # update and read
    asset.alias = "my asset"
    asset.save(user=test_user)
    saved: Asset = Asset.get_if_exists(Asset.id == asset.id)
    assert saved.alias == asset.alias

    # soft delete
    saved.delete_instance(user=test_user)
    deleted = Asset.get_if_exists(
        Asset.id == saved.id,
        include_deleted_records=True
    )
    assert deleted.id == saved.id
    assert deleted.status == deleted.statuses.DELETED

    # public should be None
    public = Asset.get_if_exists(Asset.id == saved.id)
    assert public is None

    # permanent delete
    deleted.delete_instance(user=test_user, permanently=True)
    exists = Asset.get_if_exists(Asset.id == asset.id, include_deleted_records=True)
    assert exists is None


def test_write_to_bucket(test_user, asset_class: AssetClass):
    # use a fixed id incase we want to visually inspect the asset in the bucket
    # toggle ids for asset-class and asset to test the alias
    asset_id = "b2e551a2-819f-4288-b2c2-8fcab397f500"
    asset: Asset = Asset.create(user=test_user.username, asset_class=asset_class, id=asset_id)
    asset.alias = "my-asset-alias-5"
    asset.write_to_bucket(alias=True)


def test_append_list_asset_conditions():
    query = Asset.select()
    seq_id = 1
    owner = "test"
    alias = "test"
    search_by = "test"
    query = Asset._append_list_asset_conditions(query, seq_id, owner, alias, search_by)
    assert query.where() == (Asset.seq_id.cast('text') == seq_id) & (Asset.owner == owner) & (Asset.alias == alias)
    assert query.where() == (Asset.alias.contains(search_by)) | (Asset.owner.contains(search_by)) | (
            Asset.seq_id.cast('text') == search_by)
