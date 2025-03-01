import os
import copy
import pytest
from server_core.models.content import Content
from server_core.models.object import Object
from server_core.utils.file_utils import FileUtils
from server_core.utils import time_it
from server_core.models.utils import delete_records_with_ids


@pytest.fixture(scope="module")
def test_data(test_app):
    """need the test app so that db operations can be peformed"""
    return {
        "id": "gs:md5_placeholder_001=::ai_jobs/hparam_test/hparam.yml",
        "url_id": None,
        "created_by": None,
        "created_at": "2022/12/02 19-00-03 +0000",
        "content": {
            "id": "gs:md5_placeholder_001==",
            "mime_type": "application/octet-stream",
            "hash": "md5_placeholder_001==",
            "size": 560,
            "meta": {
                "type": "gcs",
                "src": "gs://placeholder-bucket/path/to/hparam.yml",
                "proxy": False
            },
            "created_by": None,
            "created_at": None
        }
    }


@pytest.fixture(scope="module")
def content_record(test_user, test_data):
    record = Content.create(user=test_user, **test_data.get("content"))
    yield record
    record.delete_instance(user=test_user, permanently=True)


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "object" in tables


def test_crud_operations(test_user, test_data, content_record):
    data = copy.deepcopy(test_data)
    data["content"] = content_record
    # create
    record = Object.create(user=test_user.username, **data)
    assert record and record.created_by == test_user.username and record.content == content_record

    # update, should throw error
    with pytest.raises(Exception) as e:
        record.created_by = "user1"
        record.save(user="user1")
    assert str(e.value) == Object.read_only_error()

    # read and check
    saved = Object.get_if_exists(Object.id == record.id)
    assert saved.content.id == record.content.id
    assert saved.id == record.id
    assert saved.status == saved.statuses.PUBLIC

    # soft delete and check
    saved.delete_instance(user=test_user.username)
    soft_del = Object.get_if_exists(Object.id == record.id, include_deleted_records=True)
    assert soft_del.status == soft_del.statuses.DELETED
    assert soft_del.soft_delete_by == test_user.username

    # public should be None
    public = Object.get_if_exists(Object.id == record.id)
    assert public is None

    # permanent delete
    Object.delete(user=test_user.username, permanently=True).where(Object.id << {saved.id}).execute()
    # saved.delete_instance(user=test_user, permanently=True)
    exists = Object.get_if_exists(Object.id == record.id, include_deleted_records=True)
    assert exists is None


def test_to_dict(test_user, test_data, content_record):
    data = copy.deepcopy(test_data)
    data["content"] = content_record
    # create
    record = Object.create(user=test_user.username, **data)
    assert record and record.created_by == test_user.username and record.content == content_record

    object_data = record.to_dict(recurse=True)
    content_data = content_record.to_dict()

    keys = [
        'id',
        'mime_type',
        'meta'
    ]

    for key in keys:
        assert object_data.get("content").get(key) == content_data.get(key)


def test_profile_batch_create(test_user):
    path = os.path.join(os.path.dirname(__file__), "genia_data.json")
    objects_data = FileUtils.read_json(path)
    contents_data = []
    for data in objects_data:
        content = copy.deepcopy(data["content"])
        data["content"] = content["id"]
        contents_data.append(content)

    with time_it("batch-create-content"):
        content_ids = Content.batch_insert(user=test_user.username, data=contents_data)
        print(f"#contents:{len(content_ids)}")

    with time_it("batch-create-object"):
        object_ids = Object.batch_insert(user=test_user.username, data=objects_data)
        assert len(object_ids) == len(objects_data)
        print(f"#ojects:{len(object_ids)}")

    with time_it("batch-create-object2"):
        object_ids2 = Object.batch_insert(user=test_user.username, data=objects_data)
        print(f"#ojects2:{len(object_ids2)}")
        # if it exists then bulk_insert should not create new
        assert len(object_ids2) == 0

    # cleanup
    with time_it("delete"):
        for id in object_ids:
            Object.delete(user=test_user, permanently=True).where(Object.id == id)
        for id in content_ids:
            Content.delete(user=test_user, permanently=True).where(Content.id == id)