import os
import shutil
from datetime import datetime
from unittest.mock import patch

import google.cloud.storage  # type: ignore[import]
from cloud_storage_mocker import Mount
from cloud_storage_mocker import patch as gcs_patch

from asset_plugin_gcs.transporter import AsyncGcsTransporter
from asset_plugin_gcs.transporter.gcs_transport_resource import GcsDownloadResource, GcsUploadResource, GcsCopyResource


class MockAsyncStorage:
    def __init__(self, session, service_file):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        self.mock_bucket = os.path.join(root_dir, "test_data", "mock_bucket")
        self.mounts = [Mount(bucket_name="test_bucket", directory=self.mock_bucket, readable=True, writable=True)]

    async def download_to_filename(self, bucket, object_name, filename, **kwargs):
        with gcs_patch(self.mounts):
            client = google.cloud.storage.Client()
            blob = client.bucket(bucket).blob(object_name)
            blob.download_to_filename(filename)

    async def upload_from_filename(self, bucket, object_name, filename, **kwargs):
        with gcs_patch(self.mounts):
            client = google.cloud.storage.Client()
            blob = client.bucket(bucket).blob(object_name)
            blob.upload_from_filename(filename)

    async def copy(self, bucket, object_name, destination_bucket, new_name, **kwargs):
        with gcs_patch(self.mounts):
            client = google.cloud.storage.Client()
            blob = client.bucket(destination_bucket).blob(new_name)
            blob.upload_from_filename(os.path.join(self.mock_bucket, object_name))


def datetime_string(date: datetime):
    return date.strftime("%m-%d-%Y_%H-%M-%S")


def test_download(project_root):
    urls = [
        "gs://test_bucket/sample_yamls/model.yml",
        "gs://test_bucket/sample_yamls/invoice.yaml",
        "gs://test_bucket/sample_yamls/sample3.yaml",
        "gs://test_bucket/sample_csvs/customers.csv",
        "gs://test_bucket/sample_csvs/income.csv"
    ]
    date_string = datetime_string(date=datetime.now())
    download_dir = os.path.join(project_root, "test_data", "download_test", date_string)
    targets = []
    for url_string in urls:
        dst = os.path.join(download_dir, os.path.basename(url_string))
        res = GcsDownloadResource(src=url_string, dst=dst)
        targets.append(res)
    # download with mock storage
    with patch("asset_plugin_gcs.transporter.async_gcs.async_download.AsyncStorage", new=MockAsyncStorage):
        transport = AsyncGcsTransporter.shared()
        transport.download(resources=targets)
    # verify
    for target in targets:
        assert os.path.exists(target.dst)
    # cleanup
    shutil.rmtree(download_dir)


def test_upload(project_root, mock_bucket):
    files = [
        "test_data/file_types/yamls/model.yml",
        "test_data/file_types/yamls/invoice.yaml",
        "test_data/file_types/yamls/sample3.yaml",
        "test_data/file_types/csvs/customers.csv",
        "test_data/file_types/csvs/income.csv"
    ]
    date_string = datetime_string(date=datetime.now())
    upload_url = os.path.join("gs://test_bucket/", date_string)
    targets = []
    for file in files:
        dst = os.path.join(upload_url, os.path.basename(file))
        res = GcsUploadResource(src=os.path.join(project_root, file), dst=dst)
        targets.append(res)
    # upload with mock storage
    with patch("asset_plugin_gcs.transporter.async_gcs.async_upload.AsyncStorage", new=MockAsyncStorage):
        transport = AsyncGcsTransporter.shared()
        transport.upload(resources=targets)
    # verify
    for target in targets:
        target_path = os.path.join(mock_bucket, date_string, os.path.relpath(target.dst, upload_url))
        assert os.path.exists(target_path)
    # cleanup
    shutil.rmtree(os.path.join(mock_bucket, date_string))


def test_copy(mock_bucket):
    urls = [
        "gs://test_bucket/sample_yamls/model.yml",
        "gs://test_bucket/sample_yamls/invoice.yaml",
        "gs://test_bucket/sample_yamls/sample3.yaml",
        "gs://test_bucket/sample_csvs/customers.csv",
        "gs://test_bucket/sample_csvs/income.csv"
    ]
    date_string = datetime_string(date=datetime.now())
    copy_url = os.path.join("gs://test_bucket/", date_string)
    targets = []
    for url_string in urls:
        dst = os.path.join(copy_url, os.path.basename(url_string))
        res = GcsCopyResource(src=url_string, dst=dst)
        targets.append(res)
    # copy with mock storage
    with patch("asset_plugin_gcs.transporter.async_gcs.async_copy.AsyncStorage", new=MockAsyncStorage):
        transport = AsyncGcsTransporter.shared()
        transport.copy(resources=targets)
    # verify
    for target in targets:
        target_path = os.path.join(mock_bucket, date_string, os.path.basename(target.dst))
        assert os.path.exists(target_path)
    # cleanup
    shutil.rmtree(os.path.join(mock_bucket, date_string))
