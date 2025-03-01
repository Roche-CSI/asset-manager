import pytest
import os
from peewee import ModelTupleCursorWrapper
from server_core import models
from server_core.utils.file_utils import FileUtils
from server_core.models.utils import delete_records


def data():
    """need the test_app fixture for making db transactions"""
    path = os.path.join(os.path.dirname(__file__), "from_client.json")
    return FileUtils.read_json(path)


def test_asset_commit(test_project, test_user):
    from_client = data()
    class_data: dict = from_client.pop("asset_class")
    project_id = class_data.pop("project")
    # create asset-class
    asset_class = models.AssetClass.get_or_none(models.AssetClass.id == project_id)
    if not asset_class:
        asset_class = models.AssetClass.create(id=class_data["id"],
                                               name=class_data["name"],
                                               project=test_project.id,
                                               user=test_user.username)

    # create contents
    objects_data: list = from_client.pop("objects")
    contents_data = []
    for obj_data in objects_data:
        content = obj_data.pop("content")
        content["created_by"] = obj_data["created_by"]
        content["created_at"] = models.Content.time_now()
        contents_data.append(content)
        obj_data["content"] = content["id"]
        obj_data["created_at"] = models.Object.time_now()
        obj_data["url_id"] = FileUtils.url_safe_md5(FileUtils.string_md5(obj_data["id"], b64=True))

    content_insert: ModelTupleCursorWrapper = models.Content.insert_many(contents_data).on_conflict_ignore().execute()
    content_ids = set(map(lambda x: x[0], content_insert))
    assert len(contents_data) == len(content_ids)
    for content in contents_data:
        assert content["id"] in content_ids

    # create content refs
    content_refs_data = []
    for cont_data in contents_data:
        content_refs_data.append({
            "asset_class": asset_class,
            "content": cont_data.get("id"),
            "created_by": cont_data.get("created_by"),
            "created_at": models.AssetClassContentRelations.time_now()
        })
    asset_class_content_rel_insert: ModelTupleCursorWrapper = models.AssetClassContentRelations.insert_many(
        content_refs_data).on_conflict_ignore().execute()
    asset_class_content_rel_ids = set(map(lambda x: x[0], asset_class_content_rel_insert))
    assert len(contents_data) == len(asset_class_content_rel_ids)
    for content_ref in content_refs_data:
        content_rel = models.AssetClassContentRelations.get(
            models.AssetClassContentRelations.asset_class == content_ref["asset_class"],
            models.AssetClassContentRelations.content == content_ref["content"]
        )
        assert content_rel.id in asset_class_content_rel_ids

    # create objects
    object_insert: ModelTupleCursorWrapper = models.Object.insert_many(objects_data).on_conflict_ignore().execute()
    object_ids = set(map(lambda x: x[0], object_insert))
    for obj_data in objects_data:
        assert obj_data["id"] in object_ids

    # create asset
    version_data = from_client.pop("version")
    asset_data = from_client.copy()
    asset_record = models.Asset.get_if_exists(models.Asset.id == asset_data["id"],
                                              include_deleted_records=True)
    if not asset_record:
        asset_record = models.Asset.create(user=test_user,
                                           asset_class=asset_class.id,
                                           id=asset_data["id"],
                                           frozen=asset_data["frozen"])
    # create asset-object refs
    object_refs_data = []
    for obj_data in objects_data:
        object_refs_data.append({
            "asset": asset_record,
            "object": obj_data["id"],
            "created_by": obj_data["created_by"],
            "created_at": models.AssetObjectRelations.time_now()
        })
    asset_object_ref_insert: ModelTupleCursorWrapper = models.AssetObjectRelations.insert_many(
        object_refs_data).on_conflict_ignore().execute()
    asset_obj_ref_ids = set(map(lambda x: x[0], asset_object_ref_insert))
    for obj_ref in object_refs_data:
        obj_asset_rel = models.AssetObjectRelations.get(
            models.AssetObjectRelations.asset == obj_ref["asset"],
            models.AssetObjectRelations.object == obj_ref["object"]
        )
        assert obj_asset_rel.id in asset_obj_ref_ids

    # create version
    version_record = models.AssetVersion.create(user=version_data.get("user", test_user.username),
                                                asset=asset_record,
                                                objects=objects_data,
                                                commit_hash=version_data.get("commit_hash"),
                                                commit_message=version_data.get("commit_message"))
    assert version_record
    added = set(version_record.patch["added"])
    assert len(added) == len(object_ids)
    for obj_id in added:
        assert obj_id in object_ids


    # cleanup
    # asset-object-relations

