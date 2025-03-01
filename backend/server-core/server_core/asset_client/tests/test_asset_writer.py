import os
import pytest
from asset_client.asset import Asset
from asset_client.asset_writer import AssetWriter
from utils.file_utils import FileUtils
from models.asset_class import AssetClass as AssetClassModel
from models.asset import Asset as AssetModel
from models.object import Object as ObjectModel
from models.asset_object_relations import AssetObjectRelations
from models.content import Content as ContentModel
from models.asset_class_content_relations import AssetClassContentRelations
from models.version_counter import VersionCounter
from models.utils import delete_records
import uuid


@pytest.fixture(scope="module")
def asset_data(test_app):
    """need the test_app fixture for making db transactions"""
    path = os.path.join(os.path.dirname(__file__), "test_data.json")
    return FileUtils.read_json(path)


def get_asset_record(user, asset_data):
    asset = Asset(user=user, data=asset_data)
    asset_cls = AssetClassModel.get_if_exists(AssetClassModel.name == asset.asset_class.name) or \
                AssetClassModel.create(user=user, name=asset.asset_class.name)
    asset.asset_class.id = str(asset_cls.id)
    asset_record = AssetModel.create(user=asset.user, asset_class=asset_cls, id=asset.id)
    return asset, asset_record


def test_create_content_records(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)
    content_records = writer.create_content_records(user=test_user, contents=asset.contents)
    assert len(content_records) == len(asset.contents)
    id_mapped = {content.id: content for content in asset.contents}
    for record in content_records:
        assert id_mapped.get(record.id).id == record.id

    # cleanup
    delete_records(content_records, ContentModel, test_user)
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records(asset_record, AssetModel, test_user)
    delete_records(asset_record.asset_class, AssetClassModel, test_user)


def test_create_asset_class_content_joins(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)

    content_records = writer.create_content_records(user=test_user, contents=asset.contents)
    join_records = writer.create_asset_class_content_joins(user=test_user,
                                                           class_id=asset_record.asset_class.id,
                                                           content_records=content_records)
    id_mapped = {record.id: record for record in content_records}
    for join in join_records:
        assert join.content.id in id_mapped
        assert join.asset_class.id == asset_record.asset_class.id

    # cleanup
    delete_records(join_records, AssetClassContentRelations, test_user)
    delete_records(content_records, ContentModel, test_user)
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)  # reverse foreign key needs get
    delete_records(asset_record, AssetModel, test_user)
    delete_records(asset_record.asset_class, AssetClassModel, test_user)


def test_create_object_records(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)

    content_records = writer.create_content_records(user=test_user, contents=asset.contents)
    object_records = writer.get_create_object_records(user=test_user, objects=asset.objects)
    assert len(object_records) == len(asset.objects)
    id_mapped = {object.id: object for object in asset.objects}
    for record in object_records:
        assert id_mapped.get(record.id).id == record.id

    # clean up
    delete_records(object_records, ObjectModel, test_user)
    delete_records(content_records, ContentModel, test_user)
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records(asset_record, AssetModel, test_user)
    delete_records(asset_record.asset_class, AssetClassModel, test_user)


def test_create_asset_object_relations(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)

    content_records = writer.create_content_records(user=test_user, contents=asset.contents)
    object_records = writer.get_create_object_records(user=test_user, objects=asset.objects)
    join_records = writer.create_asset_object_joins(user=test_user,
                                                    asset_id=asset_record.id,
                                                    object_records=object_records)
    assert len(object_records) == len(join_records)
    id_mapped = {record.id: record for record in object_records}
    for join in join_records:
        assert join.object.id == id_mapped.get(join.object.id).id
        assert join.asset.id == asset_record.id

    # cleanup
    delete_records(join_records, AssetObjectRelations, test_user)
    delete_records(object_records, ObjectModel, test_user)
    delete_records(content_records, ContentModel, test_user)
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records(asset_record, AssetModel, test_user)
    delete_records(asset_record.asset_class, AssetClassModel, test_user)


def test_get_latest_asset(test_user, asset_data):
    """Should find the latest parent of the asset"""
    asset, asset_record = get_asset_record(test_user, asset_data)
    writer = AssetWriter(asset)
    # create multiple
    num_records = 10
    asset_records = []
    version_counters = []
    for i in range(num_records):
        record = AssetModel.create(user=asset.user,
                                   asset_class=asset_record.asset_class,
                                   commit_hash=uuid.uuid4().hex.encode("ascii")
                                   )
        asset_records.append(record)
        version_counters.append(record.version_counter.get())
    # make sure all seqeuence ids got incremented
    previous = asset_records[0]
    for i in range(1, len(asset_records)):
        record = asset_records[i]
        assert record.seq_id - previous.seq_id == 1
        previous = record

    # clean up
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records(version_counters, VersionCounter, test_user)
    delete_records(asset_records, AssetModel, test_user)
    delete_records(asset_record, AssetModel, test_user)
    delete_records(asset_record.asset_class, AssetClassModel, test_user)

    #
    # # recheck with half committed and half not committed
    # for (idx, record) in enumerate(asset_records):
    #     if idx > 5:
    #         record.commit_hash = None
    #         record.save(user=asset.user)
    #     print(f"{idx} - {record.id}: {record.seq_id}/{record.version} - {record.commit_hash}")
    #
    # latest = writer.get_leaf_asset(class_id=asset_cls.id, seq_id=asset.seq_id)
    # assert latest == asset_records[5]
    #
    # # make all None
    # for record in asset_records:
    #     record.commit_hash = None
    #     record.save(user=asset.user)
    #
    # latest = writer.get_leaf_asset(class_id=asset_cls.id, seq_id=asset.seq_id)
    # assert latest is None


def test_save_to_db(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)
    saved_records = writer.save_to_db()

    # make sure contents got created
    content_records = []
    for content in asset.contents:
        record = ContentModel.get_if_exists(ContentModel.id == content.id)
        assert record.id == content.id and record.meta == content.meta and record.mime_type == content.mime_type
        content_records.append(record)
    assert len(content_records) == len(asset.contents)

    # make sure asset_class content relations got created
    asset_cls_content_relations = []
    for content in asset.contents:
        relation = AssetClassContentRelations.get_if_exists(
            AssetClassContentRelations.asset_class == asset_record.asset_class.id,
            AssetClassContentRelations.content == content.id
        )
        assert relation.asset_class.id == asset_record.asset_class.id
        assert relation.content.id == content.id
        assert relation.status == relation.statuses.PUBLIC
        asset_cls_content_relations.append(relation)

    assert len(asset_cls_content_relations) == len(asset.contents)

    # make sure objects got created
    object_records = []
    for idx, obj in enumerate(asset.objects):
        record = ObjectModel.get_if_exists(ObjectModel.id == obj.id)
        assert record.id == obj.id
        assert record.url_id == idx + 1
        object_records.append(record)
    assert len(object_records) == len(asset.objects)

    # make sure asset-object-joins got created
    asset_object_relations = []
    for obj in asset.objects:
        relation = AssetObjectRelations.get(
            AssetObjectRelations.asset == asset_record,
            AssetObjectRelations.object == obj.id
        )
        assert relation.object.id == obj.id
        asset_object_relations.append(relation)

    assert len(asset_object_relations) == len(asset.objects)

    # clean up - delete all records
    # asset-object relations
    delete_records(asset_object_relations, AssetObjectRelations, test_user)
    # object records
    delete_records(object_records, ObjectModel, test_user)
    # asset-class-content relations
    delete_records(asset_cls_content_relations, AssetClassContentRelations, test_user)
    # content-records
    delete_records(content_records, ContentModel, test_user)
    # version_counters
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    # asset-record
    delete_records(asset_record, AssetModel, test_user)
    # asset-class-record
    delete_records(asset_record.asset_class, AssetClassModel, test_user)


def test_write_to_bucket(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)
    records = writer.save_to_db()
    writer.write_to_bucket(records=records)

    # clean up - delete all records
    # asset-object relations
    asset_object_relations = records["asset_object_relations"]
    delete_records(asset_object_relations, AssetObjectRelations, test_user)
    # object records
    object_records = records["object_records"]
    delete_records(object_records, ObjectModel, test_user)
    # asset-class-content relations
    asset_class_content_relations = records["asset_class_content_relations"]
    delete_records(asset_class_content_relations, AssetClassContentRelations, test_user)
    # content-records
    content_records = records["content_records"]
    delete_records(content_records, ContentModel, test_user)
    # asset-record
    asset_record = records["asset_record"]
    delete_records(asset_record.version_counter.get(), VersionCounter, test_user)
    delete_records(asset_record, AssetModel, test_user)
    # asset-class-record
    asset_class_record = records["asset_class_record"]
    delete_records([asset_class_record], AssetClassModel, test_user)


def test_retrieve_from_db(test_user, asset_data):
    asset, asset_record = get_asset_record(user=test_user, asset_data=asset_data)
    writer = AssetWriter(asset)
    records = writer.save_to_db()
    retrieved = writer.retrieve_from_db(asset_record.id)
    """
    "asset_class_record": asset_record,
                "asset_record": asset_record,
                "content_records": content_records,
                "asset_class_content_relations": asset_class_content_joins,
                "object_records": object_records,
                "asset_object_relations": asset_object_joins
    """
    # cleanup
    delete_records(records["asset_object_relations"], AssetObjectRelations, test_user)
    delete_records(records["object_records"], ObjectModel, test_user)
    delete_records(records["asset_class_content_relations"], AssetClassContentRelations, test_user)
    delete_records(records["content_records"], ContentModel, test_user)
    delete_records(records["version_record"], ContentModel, test_user)
    delete_records(records["asset_record"], AssetModel, test_user)
    delete_records(records["asset_class_record"], AssetClassModel, test_user)