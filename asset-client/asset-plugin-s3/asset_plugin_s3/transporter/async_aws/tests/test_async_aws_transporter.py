import os
import shutil
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from asset_plugin_s3.aws_storage import AwsStorage
from asset_plugin_s3.transporter import AsyncAwsTransporter
from asset_plugin_s3.transporter.aws_transport_resource import AwsUploadResource, AwsDownloadResource, AwsCopyResource
from asset_utils.common import exceptions
from asset_utils.utils import utils


def mock_upload_file_response():
    mock_response = MagicMock()
    mock_response.raw.raw_headers = []  # Set to a default empty list or as needed
    mock_response.status_code = 200
    return mock_response


def datetime_string(date: datetime):
    return date.strftime("%m-%d-%Y_%H-%M-%S")


def test_upload(project_root: str, upload_test_url, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage, \
            patch('aioboto3.Session.client') as mock_client:
        mock_s3_client = MagicMock()
        mock_client.return_value = mock_s3_client
        mock_s3_client.upload_file = MagicMock(return_value=mock_upload_file_response())

        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        files = [
            "test_data/file_types/nested/csvs/datagroup.csv",
            "test_data/file_types/nested/csvs/datagroup_0922.csv",
            "test_data/file_types/nested/csvs/datagroup_0923.csv",
            "test_data/file_types/nested/csvs/datagroup_0924.csv",
            "test_data/file_types/nested/csvs/datagroup_0929.csv",
            "test_data/file_types/nested/csvs/txts/yamls/jsons/h5s/multi_ubf.h5"
        ]

        date_string = datetime_string(date=datetime.now())
        upload_url = upload_test_url.format(date_string=date_string)
        base_dir = "test_data/file_types/nested/csvs/"
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

        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials

        files = [
            "test_data/file_types/nested/csvs"
        ]

        date_string = datetime_string(date=datetime.now())
        upload_url = upload_test_url.format(date_string=date_string)
        base_dir = os.path.join(project_root, "test_data/file_types/nested")
        targets = []

        for file in files:
            file = os.path.join(project_root, file)
            sources = utils.files_at_location(src=file)
            for source in sources:
                dst = os.path.join(upload_url, os.path.relpath(source, base_dir))
                res = AwsUploadResource(src=os.path.join(project_root, source), dst=dst)
                targets.append(res)

        transport = AsyncAwsTransporter.shared(credentials=AwsStorage.shared().credentials)
        transport.upload(resources=targets)


def test_download(project_root, aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage:

        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        urls = [
            "s3://aws-test-bucket/rtd/asset_tool/bedf7358-1720-409a-bcdd-0094690a84b0/asset_classes/class_list.yaml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/model.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/annotate_params.yaml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/git_commit_info_ckpt0.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/run_config_ckpt0.yml",
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/training.yml"
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
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/pycharm-edu-2022.2.2.dmg": 7,
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/model.yml": 7,
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/annotate_params.yaml": 7,
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/training.yml": 7,
            "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/pycharm-professional-2023.2.1.dmg": 7,
        }

        date_string = datetime_string(date=datetime.now())
        copy_base_url = copy_test_url.format(date_string=date_string)
        targets = []

        for url, size in urls.items():
            dst = os.path.join(copy_base_url, os.path.basename(url))
            res = AwsCopyResource(src=url, dst=dst, size=size)
            targets.append(res)

        transport: AsyncAwsTransporter = AsyncAwsTransporter.shared(
            credentials=mock_Aws_Storage.return_value.credentials)
        start_time = time.time()
        transport.copy(resources=targets)
        print("--- Total time to copy", time.time() - start_time, "seconds ---")
        mock_multi_part_copy.assert_called()


def test_update_multipart_blobs(aws_test_credentials):
    with patch('asset_pluggy.storage.storage_credentials.StorageCredentials.shared') as mock_shared_storage, \
            patch('asset_plugin_s3.aws_storage.AwsStorage.shared') as mock_Aws_Storage:

        # Mock AwsStorage credentials
        mock_Aws_Storage.return_value.credentials = aws_test_credentials
        mock_shared_storage.return_value.credentials = aws_test_credentials
        url = "s3://aws-test-bucket/rtd/asset_tool/test_data/asset_client/sample_files/"
        expected = {
            'annotate_params.yaml': 2925,
            'git_commit_info_ckpt0.yml': 124,
            'model.yml': 483,
            'run_config_ckpt0.yml': 8445,
            'training.yml': 9022,
            'pycharm-edu-2022.2.2.dmg': 8388608,
            'pycharm-professional-2023.2.1.dmg': 8388608,
        }

        transport: AsyncAwsTransporter = AsyncAwsTransporter.shared(
            credentials=mock_Aws_Storage.return_value.credentials)
        blobs = AwsStorage.shared().list_blobs(url=url)
        transport.update_multipart_blobs(blobs=blobs)

        for blob in blobs:
            try:
                assert blob.multipart_size == expected.get(blob.path_in_asset)
            except exceptions.AssetException:
                pytest.fail("Multipart size not updated")
