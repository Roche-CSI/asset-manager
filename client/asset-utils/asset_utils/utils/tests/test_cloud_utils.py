from unittest.mock import patch

import pytest

from asset_utils.common.exceptions import InsufficientCredentialError, InvalidObjectSourceError
from asset_utils.utils.cloud_utils import parse_gcr_sha_url, parse_gcr_tag_url


@pytest.fixture(scope="session")
def gcr_response_success():
    return {
        "child": [],
        "manifest": {
            "sha256:abcd1234": {
                "imageSizeBytes": "123456",
                "mediaType": "application/json",
                "tag": ["latest", "stable"]
            }
        },
        "name": "test-project/test-image",
        "tags": ["latest", "stable"]
    }


@patch('asset_utils.utils.cloud_utils.get_gcr_url')
def test_parse_gcr_sha_url_success(mock_get_gcr_url, gcr_response_success):
    mock_get_gcr_url.return_value = gcr_response_success
    expected = {
        "imageSizeBytes": "123456",
        "mediaType": "application/json",
        "tag": ["latest", "stable"],
        "hash_type": "sha256",
        "hash_value": "abcd1234",
        "name": "test-project/test-image"
    }
    result = parse_gcr_sha_url("gcr.io/test-project/test-image", "sha256:abcd1234")
    assert result == expected


@patch('asset_utils.utils.cloud_utils.get_gcr_url')
def test_parse_gcr_sha_url_permission_error(mock_get_gcr_url):
    mock_get_gcr_url.return_value = {"errors": [{"code": "DENIED"}]}
    with pytest.raises(InsufficientCredentialError):
        parse_gcr_sha_url("gcr.io/test-project/test-image", "sha256:nonexistent")


@patch('asset_utils.utils.cloud_utils.get_gcr_url')
def test_parse_gcr_sha_url_not_found(mock_get_gcr_url):
    mock_get_gcr_url.return_value = {}
    with pytest.raises(InvalidObjectSourceError):
        parse_gcr_sha_url("gcr.io/test-project/nonexistent", "sha256:nonexistent")


@patch('asset_utils.utils.cloud_utils.get_gcr_url')
def test_parse_gcr_tag_url_success(mock_get_gcr_url, gcr_response_success):
    mock_get_gcr_url.return_value = gcr_response_success
    expected = {
        "imageSizeBytes": "123456",
        "mediaType": "application/json",
        "tag": ["latest", "stable"],
        "hash_type": "sha256",
        "hash_value": "abcd1234",
        "name": "test-project/test-image"
    }
    result = parse_gcr_tag_url("gcr.io/test-project/test-image:latest")
    assert result == expected


@patch('asset_utils.utils.cloud_utils.get_gcr_url')
def test_parse_gcr_tag_url_permission_error(mock_get_gcr_url):
    mock_get_gcr_url.return_value = {"errors": [{"code": "DENIED"}]}
    with pytest.raises(InsufficientCredentialError):
        parse_gcr_tag_url("gcr.io/test-project/test-image:latest")


@patch('asset_utils.utils.cloud_utils.get_gcr_url')
def test_parse_gcr_tag_url_not_found(mock_get_gcr_url):
    mock_get_gcr_url.return_value = {}
    with pytest.raises(InvalidObjectSourceError):
        parse_gcr_tag_url("gcr.io/test-project/test-image:nonexistent")
