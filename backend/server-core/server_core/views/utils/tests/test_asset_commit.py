import os
from datetime import datetime
from server_core import models
from server_core.utils.file_utils import FileUtils
from server_core.models.utils import delete_records, delete_records_with_ids
from server_core.views.utils.asset_commit import AssetCommit
from server_core.views.utils.commit_data import CommitData
from server_core.utils import time_it


def data():
    """need the test_app fixture for making db transactions"""
    path = os.path.join(os.path.dirname(__file__), "from_client.json")
    return FileUtils.read_json(path)


def large_asset_data():
    objects_data = FileUtils.read_json(os.path.join(os.path.dirname(__file__), "genia_data.json"))
    asset_data = data()
    asset_data["objects"] = objects_data
    return asset_data


def save_asset_data(data: dict, project_id: str, username: str) -> CommitData:
    class_data: dict = data.get("asset_class")
    class_data["project"] = project_id
    objects_data: list = data.get("objects")
    version_data: dict = data.get("version")
    asset_class = models.AssetClass.create(id=class_data["id"],
                                           name=class_data["name"],
                                           project=project_id,
                                           user=username)

    commit = AssetCommit(data=data, username=username)
    saved: CommitData = commit.save_to_db()
    return saved, objects_data, version_data


def test_asset_commit(test_project, test_user):
    from_client = data()
    saved, objects_data, version_data = save_asset_data(data=from_client,
                                                        project_id=test_project.id,
                                                        username=test_user.username)

    # compare asset-class
    assert type(saved) is CommitData
    assert saved.asset_class.project.id == test_project.id
    # compare asset
    assert str(saved.asset.id) == from_client["id"]
    # compare contents
    contents_data = list(map(lambda x: x["content"], objects_data))  # one content per object
    assert len(saved.content_ids) == len(contents_data)
    for content in contents_data:
        assert content["id"] in saved.content_ids

    # compare asset_class-content relations
    assert len(saved.content_rel_ids) == len(contents_data)

    # compare objects
    assert len(saved.object_ids) == len(objects_data)
    for obj_data in objects_data:
        assert obj_data["id"] in saved.object_ids

    # asset-object relations
    assert len(saved.object_rel_ids) == len(objects_data)

    # version
    added = saved.version.patch["added"]
    assert len(added) == len(saved.object_ids)
    assert saved.version.commit_hash == version_data["commit_hash"]
    assert saved.version.commit_message == version_data["commit_message"]
    # delete created records
    cleanup_saved_records(username=test_user.username, saved=saved)


def test_serialize(test_project, test_user):
    from_client = data()
    test_project.remote_url = os.path.join("gs://placeholder_bukcet/test/server")
    with test_project.storage(server=True):
        saved, _, _ = save_asset_data(data=from_client,
                                      project_id=test_project.id,
                                      username=test_user.username)
        saved.serialize()
        assert saved.json_data and saved.bucket_data
        cleanup_saved_records(username=test_user.username, saved=saved)


def test_write_to_bucket(test_project, test_user):
    from_client = data()
    urls = [
        ("gs://placeholder_bukcet/test/server", "GOOGLE_APPLICATION_CREDENTIALS"),
        ("s3://placeholder_bukcet/tests/server", "AWS_CREDENTIALS")
    ]
    saved, _, _ = save_asset_data(data=from_client, project_id=test_project.id, username=test_user.username)
    for url, cred_var in urls:
        test_project.remote_url = os.path.join(url, datetime.now().isoformat())
        test_project.credentials_server = FileUtils.read_json(os.environ[cred_var])
        with test_project.storage(server=True):
            saved.serialize()
            saved.write_to_bucket(storage_url=test_project.remote_url)
    # cleanup
    cleanup_saved_records(username=test_user.username, saved=saved)


def profile_large_asset(test_project, test_user):
    large_asset = large_asset_data()
    with time_it("saving-large-asset"):
        saved, _, _ = save_asset_data(data=large_asset,
                                      project_id=test_project.id,
                                      username=test_user.username)
    test_project.remote_url = f"gs://placeholder_bukcet/test/server/{test_project.id}"
    test_project.credentials_server = FileUtils.read_json(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    with test_project.storage(server=True):
        with time_it("serialize"):
            saved.serialize()
        with time_it("write to bucket"):
            saved.write_to_bucket(storage_url=test_project.remote_url)

def cleanup_saved_records(username, saved: CommitData):
    # delete version
    delete_records(records=saved.version, model_class=models.AssetVersion, user=username)
    # delete asset
    delete_records(records=saved.asset, model_class=models.Asset, user=username)
    # delete objects
    delete_records_with_ids(record_ids=saved.object_ids, model_class=models.Object, user=username)
    # delete asset-object relations
    delete_records_with_ids(record_ids=saved.object_rel_ids, model_class=models.AssetObjectRelations, user=username)
    # content record id
    delete_records_with_ids(record_ids=saved.content_ids, model_class=models.Content, user=username)
    # asset-class content relations
    delete_records_with_ids(record_ids=saved.content_rel_ids, model_class=models.AssetClassContentRelations,
                            user=username)
    # asset-class
    delete_records(records=saved.asset_class, model_class=models.AssetClass, user=username)
