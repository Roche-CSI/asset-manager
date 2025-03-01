import os
import pytest
from server_core.models.content import Content
from server_core.utils import time_it
from server_core.utils.file_utils import FileUtils


@pytest.fixture(scope="module")
def test_data(test_app):
    """need the test app so that db operations can be peformed"""
    return {
        "id": "gs:md5_placeholder_001==",
        "mime_type": "application/octet-stream",
        "hash": "md5_placeholder_001==",
        "size": 560,
        "meta": {
            "type": "gcs",
            "src": "gs://placeholder-bucket/path/to/hparam.yml",
            "proxy": False
        },
    }


def test_table_exists(test_server):
    tables = test_server.db.get_tables()
    assert "content" in tables


def test_crud_ops(test_user, test_data):
    """Create, Read, Update and Delete"""
    # 1. create record
    record = Content.create(user=test_user.username, **test_data)
    assert record
    for key in test_data:
        assert hasattr(record, key)
    assert record.status == record.statuses.PUBLIC
    assert record.created_by == test_user.username
    assert record.created_at is not None

    # 2.  update, should raise exception
    with pytest.raises(Exception) as e:
        record.mime_type = "application/json"
        record.save(user=test_user)
    assert e

    # 3. soft delete
    record.delete_instance(user=test_user.username)
    soft_del = Content.get_if_exists(Content.id == record.id, include_deleted_records=True)
    assert soft_del.status == soft_del.statuses.DELETED
    assert soft_del.soft_delete_by == test_user.username

    # 4. public
    public = Content.get_if_exists(Content.id == record.id)
    assert public is None

    # 4. permanent delete
    record.delete_instance(user=test_user, permanently=True)
    deleted = Content.get_if_exists(Content.id == record.id, include_deleted_records=True)
    assert deleted is None


def profile_create(test_user):
    """for profiling large writes"""
    path = os.path.join(os.path.dirname(__file__), "genia_data.json")
    objects_data = FileUtils.read_json(path)
    contents_data = list(map(lambda x: x["content"], objects_data))
    with time_it("create"):
        for data in contents_data:
            record = Content.get_or_none(Content.id == data["id"])
            if not record:
                record = Content.create(user=test_user.username, **data)
            assert isinstance(record, Content)


def profile_batch_create(test_user):
    """for profiling large writes"""
    path = os.path.join(os.path.dirname(__file__), "genia_data.json")
    objects_data = FileUtils.read_json(path)
    contents_data = list(map(lambda x: x["content"], objects_data))
    with time_it("batch-create"):
        record_ids = Content.batch_insert(user=test_user.username, data=contents_data)
        print(len(record_ids))
