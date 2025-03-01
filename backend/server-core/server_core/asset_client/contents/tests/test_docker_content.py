from asset_client.contents.content_factory import ContentFactory
from asset_client.contents.docker_content import DockerContent

DATA = {
    "id": "gcr:sha256$0000000000000000000000000000000000000000000000000000000000000000",
    "mime_type": "application/vnd.docker.distribution.manifest.v2+json",
    "size": "2531814435",
    "meta": {
        "type": "gcr",
        "src": "gcr.io/placeholder-project/placeholder-image@sha256:0000000000000000000000000000000000000000000000000000000000000000" ,
        "proxy": True
    },
    "created_by": None,
    "created_at": None
}


def test_deserialize(client_asset):
    asset = client_asset
    content = DockerContent.de_serialize(asset, DATA)
    assert content.id == DATA["id"]
    assert content.hash_type == "sha256"
    assert content.hash_value == "0000000000000000000000000000000000000000000000000000000000000000"

    # try through ContentFactory
    content = ContentFactory().de_serialize(asset=asset, data=DATA)
    assert content.id == DATA["id"]
    assert content.hash_type == "sha256"
    assert content.hash_value == "0000000000000000000000000000000000000000000000000000000000000000"
