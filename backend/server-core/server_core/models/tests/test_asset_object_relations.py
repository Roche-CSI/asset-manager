import pytest
from server_core.models.asset import Asset
from server_core.models.object import Object
from server_core.models.content import Content
from server_core.models.asset_object_relations import AssetObjectRelations
from server_core.asset_client.objects.object import Object as ClientObject


@pytest.fixture(scope="module")
def asset(test_user, test_asset_class):
    asset: Asset = Asset.create(user=test_user, asset_class=test_asset_class)
    yield asset
    asset.delete_instance(user=test_user, permanently=True)
    assert Asset.get_if_exists(Asset.id == asset.id, include_deleted_records=True) is None


@pytest.fixture(scope="module")
def content_record(test_user, test_app):
    content = Content.create(user=test_user, **{
        "id": "gs:md5$placeholder_id_003==",
        "hash": "md5$placeholder_id_003==",
        "mime_type": "image/jpeg",
    })
    yield content
    content.delete_instance(user=test_user, permanently=True)
    assert Content.get_if_exists(Content.id == content.id, include_deleted_records=True) is None


@pytest.fixture(scope="module")
def object(test_user, content_record):
    obj = Object.create(user=test_user, content=content_record, id=ClientObject.create_id(content_record.id, "mypath/ab.img"))
    yield obj
    obj.delete_instance(user=test_user, permanently=True)
    assert Object.get_if_exists(Object.id == obj.id, include_deleted_records=True) is None


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "assetobjectrelations" in tables


def test_crud_operations(asset, object, test_user):
    # create
    relation = AssetObjectRelations.create(
        user=test_user,
        object=object,
        asset=asset
    )
    assert relation.id and relation.object == object and relation.asset == asset
    assert relation.status == relation.statuses.PUBLIC

    # read and check
    saved = AssetObjectRelations.get_if_exists(AssetObjectRelations.object == object, AssetObjectRelations.asset == asset)
    assert saved.asset == relation.asset and saved.object == relation.object
    saved.delete_instance(user=test_user)

    # update, should raise error
    with pytest.raises(Exception) as e:
        saved.created_by = "random_user"
        saved.save()
    assert str(e.value) == AssetObjectRelations.read_only_error()

    # soft delete
    saved.delete_instance(user=test_user)
    soft_del = AssetObjectRelations.get_if_exists(AssetObjectRelations.id == saved.id, include_deleted_records=True)
    soft_del.status == saved.statuses.DELETED

    # public should be None
    public = AssetObjectRelations.get_if_exists(AssetObjectRelations.id == saved.id)
    assert public is None

    # delete permanently
    soft_del.delete_instance(user=test_user, permanently=True)
    exists = AssetObjectRelations.get_if_exists(AssetObjectRelations.id == soft_del.id, include_deleted_records=True)
    assert exists is None






