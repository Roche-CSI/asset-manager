from asset_client.contents.gcs_content import GcsContent

DATA = {
    "id": "gs:md5_placeholder_md5_000==",
    "mime_type": "text/plain",
    "hash": "md5_placeholder_md5_000==",
    "size": 56839,
    "meta": {
        "src": "gs://bucket/test/client/asset_classes/00000000-000f-00b0-b0f0-0000000000a0.yaml",
        "proxy": True
    },
    "created_by": "user1",
    "created_at": '2021/10/27 10-24-06 PDT'
}


def test_can_stage(client_asset):
    asset = client_asset
    content = GcsContent.de_serialize(asset, DATA)
    assert content.id == "gs:md5_2Gg70COLj3pnRdwuI50ijg=="
    assert content.hash == "md5_2Gg70COLj3pnRdwuI50ijg=="
    assert content.hash_type == "md5"
    assert content.hash_value == "2Gg70COLj3pnRdwuI50ijg=="
    assert not content.can_stage
    assert not content.can_commit