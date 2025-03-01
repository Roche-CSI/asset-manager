from server_core.models.asset_class_content_relations import AssetClassContentRelations
from server_core.models.asset_class import AssetClass
from server_core.models.content import Content
import pytest


@pytest.fixture(scope="module")
def test_data(test_app):
    """need the test app so that db operations can be peformed"""
    return {
        "class_name": "gene_data",
        "contents": [
            ("gs:md5$placeholder_id_003==", "md5$placeholder_id_003=="),
            ("gs:md5$placeholder_id_002==", "md5$placeholder_id_002==")
        ]
    }


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "assetclasscontentrelations" in tables


def test_crud_ops(test_user, test_data, test_project):
    """Create, Read, Update and Delete"""
    # 1. create records
    relations = []
    content_records = []

    asset_class = AssetClass.get_or_create(user=test_user, name=test_data.get("class_name"), project=test_project)[0]

    for content_id, hash in test_data.get("contents"):
        content_record = Content.create(user=test_user, id=content_id, hash=hash)
        relations.append(
            AssetClassContentRelations.create(
                user=test_user,
                asset_class=asset_class.id,
                content=content_record.id
            ))
        content_records.append(content_record)
    assert len(relations) == 2

    # update, should throw error
    for record in relations:
        record.created_by = "random_user"
        with pytest.raises(Exception) as e:
            record.save()

    # get and check
    for record in content_records:
        exists = AssetClassContentRelations.get_if_exists(
            AssetClassContentRelations.asset_class == asset_class.id,
            AssetClassContentRelations.content == record.id)
        assert exists.asset_class.id == asset_class.id
        assert exists.content.id == record.id

    # soft delete and check
    for record in relations:
        record.delete_instance(user=test_user)
        soft_del = AssetClassContentRelations.get_if_exists(
            AssetClassContentRelations.asset_class == asset_class.id,
            AssetClassContentRelations.content == record.content.id,
            include_deleted_records=True
        )
        assert soft_del.status == soft_del.statuses.DELETED

        public = AssetClassContentRelations.get_if_exists(
            AssetClassContentRelations.asset_class == asset_class.id,
            AssetClassContentRelations.content == record.id
        )
        assert public is None

    # permanent delete
    for record in relations:
        record.delete_instance(user=test_user, permanently=True)
        public = AssetClassContentRelations.get_if_exists(
            AssetClassContentRelations.asset_class == asset_class.id,
            AssetClassContentRelations.content == record.content.id,
            include_deleted_records=True)
        assert public is None

    # clean up content records
    for record in content_records:
        record.delete_instance(user=test_user, permanently=True)

    # cleanup asset-class record
    asset_class.delete_instance(user=test_user, permanently=True)