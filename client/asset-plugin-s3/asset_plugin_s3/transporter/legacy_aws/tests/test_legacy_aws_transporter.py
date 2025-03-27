import os
from datetime import datetime
from unittest.mock import MagicMock, patch

from asset_plugin_s3.aws_storage import AwsStorage
from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource, AwsDownloadResource
from asset_plugin_s3.transporter.legacy_aws.legacy_aws_transporter import LegacyAwsTransporter
from asset_utils.utils import utils


def datetime_string(date: datetime):
    return date.strftime("%m-%d-%Y_%H-%M-%S")


def mock_async_upload_resource(mock_upload):
    async def inner(s3_client, resource, result):
        # Simulate a successful response with a dummy upload_id
        mock_response = MagicMock()
        mock_response.content.read = MagicMock(return_value=b"""<?xml version="1.0" encoding="UTF-8"?>
            <InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <UploadId>mock-upload-id</UploadId>
            </InitiateMultipartUploadResult>""")
        mock_upload.return_value = mock_response

    return inner


def test_upload(project_root: str, upload_test_url: str, aws_test_credentials: dict):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client, \
            patch('asset_plugin_s3.transporter.legacy_aws.async_upload.async_upload_resource') as mock_upload:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        mock_upload.side_effect = mock_async_upload_resource(mock_upload)

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

        transport = LegacyAwsTransporter.shared(credentials=AwsStorage.shared().credentials)
        transport.upload(resources=targets)
        mock_upload.assert_called()


def test_upload_dir(project_root: str, upload_test_url: str, aws_test_credentials: dict):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client, \
            patch('asset_plugin_s3.transporter.legacy_aws.async_upload.async_upload_resource') as mock_upload:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        mock_upload.side_effect = mock_async_upload_resource(mock_upload)

        date_string = datetime_string(date=datetime.now())
        upload_url = upload_test_url.format(date_string=date_string)
        base_dir = os.path.join(project_root, "test_data/file_types")
        targets = []

        for source in utils.files_at_location(src=base_dir):
            dst = os.path.join(upload_url, os.path.relpath(source, base_dir))
            res = AwsUploadResource(src=source, dst=dst)
            targets.append(res)

        transport = LegacyAwsTransporter.shared(credentials=AwsStorage.shared().credentials)
        transport.upload(resources=targets)
        mock_upload.assert_called()


def mock_download_resource(mock_async_download):
    async def inner(s3_client, resource: AwsDownloadResource, result: list):
        # Simulate a successful response with a dummy upload_id
        mock_response = MagicMock()
        mock_response.raw.raw_headers = []  # Set to a default empty list or as needed
        mock_response.status_code = 200
        return mock_response

    return inner


def test_download(project_root, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client, \
            patch(
                'asset_plugin_s3.transporter.legacy_aws.async_download.__async_download_resource') as mock_async_download:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        mock_async_download.side_effect = mock_download_resource(mock_async_download)

        urls = [
            "s3://aws-test-bucket/test_data/sample_files/file1.yml",
            "s3://aws-test-bucket/test_data/sample_files/file2.yaml",
            "s3://aws-test-bucket/test_data/sample_files/file3.yml",
            "s3://aws-test-bucket/test_data/sample_files/file4.yml"
        ]

        date_string = datetime_string(date=datetime.now())
        download_dir = os.path.join(project_root, "test_data", "download_test", date_string)
        os.makedirs(download_dir, exist_ok=True)
        targets = []
        for url_string in urls:
            dst = os.path.join(download_dir, os.path.basename(url_string))
            res = AwsDownloadResource(src=url_string, dst=dst)
            targets.append(res)

        transport = LegacyAwsTransporter.shared(credentials=AwsStorage.shared().credentials)
        transport.download(resources=targets)
        mock_async_download.assert_called()
