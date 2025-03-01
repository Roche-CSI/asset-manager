import os
from asset_client.contents.file_content import FileContent

DATA = {
    "id": "gs:md5$placeholder_id_002==",
    "mime_type": "file",
    "created_by": "user1",
    "created_at": '2021-10-27T10-24-06-PDT'
}


def test_deserialize(client_asset):
    asset = client_asset
    content = FileContent.de_serialize(asset, DATA)
    assert content.id == "gs:md5$placeholder_id_002=="
    assert content.hash == "md5$placeholder_id_002=="
    assert content.hash_type == "md5"
    assert content.hash_value == "placeholder_id_002=="


def test__hashing(client_asset):
    asset = client_asset
    assert FileContent(asset=asset, **DATA) == FileContent(asset=asset, **DATA)


def test_serialize(client_asset):
    asset = client_asset
    content = FileContent.de_serialize(asset=asset, data=DATA)
    serialized = content.serialize()
    # make sure all serialized keys are there
    for key in FileContent.serialize_fields():
        assert key in serialized

    for key in DATA:
        assert serialized[key] == DATA[key]


def test_urls(client_asset):
    asset = client_asset
    asset.class_name = "test_asset"
    asset.class_id = "test_asset"
    for content in asset.contents:
        print(content.remote_url)
        print(content.staging_url)