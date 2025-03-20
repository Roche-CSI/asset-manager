import os.path
from unittest.mock import patch

import boto3
import moto
import pytest

from asset_pluggy.storage import BlobStoreURL
from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_plugin_s3.aws_blob import AwsBlob
from asset_plugin_s3.aws_storage import AwsStorage
from asset_utils.utils import time_it


@pytest.fixture(scope='function')
def mock_s3():
    with moto.mock_aws():
        # Set up mock S3 client
        s3 = boto3.client('s3', region_name='us-east-1',
                          aws_access_key_id='mock_access_key',
                          aws_secret_access_key='mock_secret_key')
        # Create a test bucket and upload test objects
        bucket_name = 'aws-test-bucket'
        s3.create_bucket(Bucket=bucket_name)

        urls = [
            "s3://aws-test-bucket/test_data/sample_files/file1.yml",
            "s3://aws-test-bucket/test_data/sample_files/file2.yaml",
            "s3://aws-test-bucket/test_data/sample_files/file3.yml",
            "s3://aws-test-bucket/test_data/sample_files/file4.yml",
        ]
        for url in urls:
            _, key = url.replace("s3://", "").split("/", 1)
            s3.put_object(Bucket=bucket_name, Key=key, Body=b'content')

        yield urls  # Provide URLs for tests


def test_get_blob(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        urls = [
            "s3://aws-test-bucket/test_data/sample_files/file1.yml",
            "s3://aws-test-bucket/test_data/sample_files/file2.yaml",
            "s3://aws-test-bucket/test_data/sample_files/file3.yml",
            "s3://aws-test-bucket/test_data/sample_files/file4.yml",
        ]
        expected = [
            {
                "bucket": "aws-test-bucket",
                "name": "test_data/sample_files/file1.yml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            },
            {
                "bucket": "aws-test-bucket",
                "name": "test_data/sample_files/file2.yaml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            },
            {
                "bucket": "aws-test-bucket",
                "name": "test_data/sample_files/file3.yml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            },
            {
                "bucket": "aws-test-bucket",
                "name": "test_data/sample_files/file4.yml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            }
        ]

        for idx, url in enumerate(urls):
            blob: AwsBlob = AwsStorage.shared().get_blob(url_string=url)
            exp = expected[idx]
            for key in exp:
                assert exp[key] == getattr(blob, key)


def test_list_blobs(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        data = [
            ("s3://aws-test-bucket/test_data/sample_files/", "AWS_DP_CREDENTIALS", 4,
             "application/x-yaml"),
        ]
        prev = StorageCredentials.shared().credentials
        for url, cred_file, count, content_type in data:
            cred_data = cred_file
            StorageCredentials.shared().set_credentials(cred=cred_data)
            ignore = None
            _, file_ext = os.path.splitext(url)
            blobs = AwsStorage.shared().list_blobs(url=url, ignore=ignore)
            _, ignore_ext = os.path.splitext(ignore) if ignore else (None, None)
            assert len(blobs) == count
            for blob in blobs:
                assert isinstance(blob, AwsBlob)
                if file_ext:
                    assert blob.name.endswith(file_ext)
                if ignore_ext:
                    assert not blob.name.endswith(ignore_ext)
                assert blob.content_type == content_type
                assert blob.is_file

        StorageCredentials.shared().credentials = prev


def test_profile_list_blobs(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        TIME_IT = True
        if TIME_IT:
            with time_it("aws_list_blobs"):
                url = "s3://aws-test-bucket/00000000-0000-0000-0000-000000000001/" \
                      "contents/00000000-0000-0000-0000-000000000001"
                AwsStorage.shared().list_blobs(url=url)


def test_blob_exists(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        urls = [
            ("s3://aws-test-bucket/test_data/sample_files/file1.yml", True),
            ("s3://aws-test-bucket/test_data/sample_files/file2.yaml", True),
            ("s3://aws-test-bucket/test_data/sample_files/file3.yml", True),
            ("s3://aws-test-bucket/test_data/sample_files/file4.yml", True),
            ("s3://aws-test-bucket/test_data/file5.yaml", False),
            ("s3://aws-test-bucket/test_data/file6.yml", False),
            ("s3://aws-test-bucket/test_data/file1.yml", False),
            ("s3://aws-test-bucket/test_data/test.txt", False),
            ("s3://aws-test-bucket/test_data/test.txt2", False)
        ]
        for data in urls:
            exists = AwsStorage.shared().blob_exists(url_string=data[0])
            assert exists == data[1]


def test_delete_blobs(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        urls = [
            "s3://aws-test-bucket/test_data/copy_tests/"
        ]
        for url in urls:
            blobs_list = AwsStorage.shared().list_blobs(url=url)
            print(f"found:{len(blobs_list)} blobs, proceeding to delete")
            delete_urls = list(map(lambda blob: blob.url, blobs_list))
            AwsStorage.shared().delete_blobs(url_strings=delete_urls)
            # Fetch again
            after_delete = AwsStorage.shared().list_blobs(url=url)
            assert len(after_delete) == 0


def test_signed_url(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        for url in mock_s3:
            signed_url = AwsStorage.shared().signed_url_for_blob(blob_url=url)
            gcs_url = BlobStoreURL(url=url)
            assert gcs_url.path in signed_url


def test_get_bucket_cors(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        for url in mock_s3:
            cors_config = AwsStorage.shared().get_bucket_cors(bucket_url=url)
            assert len(cors_config) == 0
