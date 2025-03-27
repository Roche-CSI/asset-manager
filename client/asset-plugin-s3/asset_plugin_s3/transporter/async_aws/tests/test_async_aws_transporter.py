import os
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch

from asset_plugin_s3.aws_storage import AwsStorage
from asset_plugin_s3.transporter import AsyncAwsTransporter
from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource, AwsDownloadResource, AwsCopyResource
from asset_utils.utils import utils


def datetime_string(date: datetime):
    return date.strftime("%m-%d-%Y_%H-%M-%S")


def mock_upload_file_response():
    mock_response = MagicMock()
    mock_response.raw.raw_headers = []  # Set to a default empty list or as needed
    mock_response.status_code = 200
    return mock_response


def test_upload(project_root: str, upload_test_url, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        mock_s3_client.upload_file = MagicMock(return_value=mock_upload_file_response())
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        files = [
            "test_data/file_types/csvs/customers.csv",
            "test_data/file_types/csvs/income.csv",
            "test_data/file_types/jsons/web_app.json",
            "test_data/file_types/yamls/model.yml"
        ]

        date_string = datetime_string(date=datetime.now())
        upload_url = upload_test_url.format(date_string=date_string)
        base_dir = "test_data/file_types"
        targets = []
        for file in files:
            dst = os.path.join(upload_url, os.path.relpath(file, base_dir))
            src = os.path.join(project_root, file)
            res = AwsUploadResource(src=src, dst=dst)
            targets.append(res)

        transport = AsyncAwsTransporter.shared(credentials=AwsStorage.shared().credentials)
        transport.upload(resources=targets)


def test_upload_dir(project_root: str, upload_test_url: str, aws_test_credentials: dict):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        mock_s3_client.upload_file = MagicMock(return_value=mock_upload_file_response())
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        date_string = datetime_string(date=datetime.now())
        upload_url = upload_test_url.format(date_string=date_string)
        base_dir = os.path.join(project_root, "test_data/file_types")
        targets = []

        for source in utils.files_at_location(src=base_dir):
            dst = os.path.join(upload_url, os.path.relpath(source, base_dir))
            res = AwsUploadResource(src=source, dst=dst)
            targets.append(res)

        transport = AsyncAwsTransporter.shared(credentials=AwsStorage.shared().credentials)
        transport.upload(resources=targets)


def test_download(project_root, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage:
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        urls = [
            "s3://aws-test-bucket/test_data/sample_files/file1.yml",
            "s3://aws-test-bucket/test_data/sample_files/file2.yaml",
            "s3://aws-test-bucket/test_data/sample_files/file3.yml",
            "s3://aws-test-bucket/test_data/sample_files/file4.yml",
            "s3://aws-test-bucket/test_data/sample_files/file5.yml"
        ]

        date_string = datetime_string(date=datetime.now())
        download_dir = os.path.join(project_root, "test_data", "download_test", date_string)
        os.makedirs(download_dir, exist_ok=True)
        targets = []
        for url_string in urls:
            dst = os.path.join(download_dir, os.path.basename(url_string))
            res = AwsDownloadResource(src=url_string, dst=dst)
            targets.append(res)

        transport = AsyncAwsTransporter.shared(credentials=mock_Aws_Storage.return_value.credentials)
        transport.download(resources=targets)
        # verify
        for target in targets:
            assert os.path.exists(target.dst)
        # cleanup
        shutil.rmtree(download_dir)


def test_copy(aws_test_credentials, copy_test_url):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client, \
            patch('asset_plugin_s3.transporter.async_aws.async_copy.__multi_part_copy') as mock_multi_part_copy:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        async def mock_multi_part_copy_function(session, credentials, resource):
            # Simulate a successful response with a dummy upload_id
            mock_response = MagicMock()
            mock_response.content.read = MagicMock(return_value=b"""<?xml version="1.0" encoding="UTF-8"?>
                <InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
                <UploadId>mock-upload-id</UploadId>
                </InitiateMultipartUploadResult>""")
            mock_multi_part_copy.return_value = mock_response

        mock_multi_part_copy.side_effect = mock_multi_part_copy_function

        urls = {
            "s3://aws-test-bucket/test_data/sample_files/file1.yml": 7,
            "s3://aws-test-bucket/test_data/sample_files/file2.yaml": 7,
            "s3://aws-test-bucket/test_data/sample_files/file3.yml": 7
        }

        date_string = datetime_string(date=datetime.now())
        copy_base_url = copy_test_url.format(date_string=date_string)
        targets = []
        for url, size in urls.items():
            dst = os.path.join(copy_base_url, os.path.basename(url))
            res = AwsCopyResource(src=url, dst=dst, size=size)
            targets.append(res)

        transport = AsyncAwsTransporter.shared(credentials=mock_Aws_Storage.return_value.credentials)
        transport.copy(resources=targets)
        mock_multi_part_copy.assert_called()


def test_update_multipart_blobs(aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage:
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        expected = {
            'file1.yaml': 2925,
            'file2.yml': 124,
            'file3.yml': 483,
            'file4.yml': 8445,
            'file5.yml': 9022,
            'test-file-2022.2.2.dmg': 8388608,
            'test-file-2023.2.1.dmg': 8388608,
        }

        transport = AsyncAwsTransporter.shared(credentials=mock_Aws_Storage.return_value.credentials)
        # Mock the list_blobs method to return test blobs
        test_blobs = [MockBlob(path, size) for path, size in expected.items()]
        mock_Aws_Storage.return_value.list_blobs.return_value = test_blobs

        transport.update_multipart_blobs(blobs=test_blobs)
        # Verify that each blob's multipart size matches the expected value
        for blob in test_blobs:
            assert blob.multipart_size == expected.get(blob.path_in_asset), \
                f"Blob {blob.path_in_asset} multipart size mismatch"


class MockBlob:
    def __init__(self, path_in_asset, multipart_size):
        self.path_in_asset = path_in_asset
        self.multipart_size = multipart_size
