import json
from unittest.mock import patch

from asset_plugin_gcr.gcr_blob import GcrBlob
from asset_plugin_gcr.gcr_storage import GcrStorage


def test_get_blob(fake_url_data):
    urls = [
        "gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "gcr.io/my-test-project/my-test-image:latest",
    ]

    expected = {
        "name": "my-test-project/my-test-image",
        "size": 2391153464,
        "content_type": "application/vnd.docker.distribution.manifest.v2+json",
        "hashes": {"sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890"},
        "tag": ["latest"],
        "host": "gcr.io",
        "url": "gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    }

    with patch("asset_plugin_gcr.gcr_mixin.GcrMixin.fetch_url_data", return_value=fake_url_data):
        for idx, url in enumerate(urls):
            blob: GcrBlob = GcrStorage.shared().get_blob(url=url)
            for key in expected:
                if type(expected[key]) is dict:
                    assert json.dumps(expected[key]) == json.dumps(getattr(blob, key))
                else:
                    assert expected[key] == getattr(blob, key)


def test_list_blobs(fake_url_data):
    urls = [
        "gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "gcr.io/my-test-project/my-test-image:latest",
    ]
    expected = {
        "name": "my-test-project/my-test-image",
        "size": 2391153464,
        "content_type": "application/vnd.docker.distribution.manifest.v2+json",
        "hashes": {"sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890"},
        "tag": ["latest"],
        "host": "gcr.io",
        "url": "gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    }

    with patch("asset_plugin_gcr.gcr_mixin.GcrMixin.fetch_url_data", return_value=fake_url_data):
        for idx, url in enumerate(urls):
            blob: GcrBlob = GcrStorage.shared().get_blob(url=url)
            for key in expected:
                if type(expected[key]) is dict:
                    assert json.dumps(expected[key]) == json.dumps(getattr(blob, key))
                else:
                    assert expected[key] == getattr(blob, key)
