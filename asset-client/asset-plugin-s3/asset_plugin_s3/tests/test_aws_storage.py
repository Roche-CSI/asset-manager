import os.path
from unittest.mock import patch

import boto3
import moto
import pytest

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
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/model.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/annotate_params.yaml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/run_config_ckpt0.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/training.yml",
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
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/model.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/annotate_params.yaml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/run_config_ckpt0.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/training.yml",
        ]
        expected = [
            {
                "bucket": "aws-test-bucket",
                "name": "rtd/asset_tool/test_data/asset_client/sample_files/model.yml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            },
            {
                "bucket": "aws-test-bucket",
                "name": "rtd/asset_tool/test_data/asset_client/sample_files/annotate_params.yaml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            },
            {
                "bucket": "aws-test-bucket",
                "name": "rtd/asset_tool/test_data/asset_client/sample_files/run_config_ckpt0.yml",
                "content_type": 'binary/octet-stream',
                "size": 7,
                "is_file": True
            },
            {
                "bucket": "aws-test-bucket",
                "name": "rtd/asset_tool/test_data/asset_client/sample_files/training.yml",
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
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/", "AWS_DP_CREDENTIALS", 4,
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
                url = "s3://aws-test-bucket/rtd/asset_tool/bedf7358-1720-409a-bcdd-0094690a84b0/" \
                      "contents/ba01e4da-6dd7-4077-9885-91ae40ab503a"
                AwsStorage.shared().list_blobs(url=url)


def test_blob_exists(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        urls = [
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/model.yml", True),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/annotate_params.yaml", True),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/run_config_ckpt0.yml", True),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/training.yml", True),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/annotate_params.yaml", False),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/git_commit_info_ckpt0.yml", False),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/model.yml", False),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/test.txt", False),
            ("s3://aws-test-bucket/rtd/asset_tool/test_data/test.txt2", False)
        ]
        for data in urls:
            exists = AwsStorage.shared().blob_exists(url_string=data[0])
            assert exists == data[1]


def test_delete_blobs(mock_s3, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage:
        # Mock AwsStorage credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        urls = [
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/copy_tests/"
        ]
        for url in urls:
            blobs_list = AwsStorage.shared().list_blobs(url=url)
            print(f"found:{len(blobs_list)} blobs, proceeding to delete")
            delete_urls = list(map(lambda blob: blob.url, blobs_list))
            AwsStorage.shared().delete_blobs(url_strings=delete_urls)
            # Fetch again
            after_delete = AwsStorage.shared().list_blobs(url=url)
            assert len(after_delete) == 0
