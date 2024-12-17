import json
import os
from unittest.mock import patch

from asset_plugin_gcs.gcs_blob import GcsBlob
from asset_plugin_gcs.gcs_storage import GcsStorage
from asset_utils.utils import list_files
from asset_utils.utils.file_utils import FileUtils

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class MockBlob:

    def __init__(self, name):
        self.name = name
        self.mock_bucket = os.path.join(ROOT_DIR, "test_data", "mock_bucket")
        metadata_file = os.path.join(self.mock_bucket, name + ".__blobdata__")
        if os.path.exists(metadata_file):
            data = FileUtils.read_json(metadata_file)
            self.md5_hash = data.get("md5_hash")
            self.crc32c = data.get("crc32c")
            self.size = data.get("size")
            self.content_type = data.get("content_type")

    def exists(self):
        return os.path.exists(os.path.join(self.mock_bucket, self.name))


class MockBucket:

    def __init__(self, name):
        self.id = name
        self.name = name
        self.path = f"/b/{name}"
        self.project_number = "123456789"
        self.mock_bucket = os.path.join(ROOT_DIR, "test_data", "mock_bucket")

    def get_blob(self, blob_name):
        return self.blob(blob_name)

    def blob(self, blob_name):
        mock_blob = MockBlob(blob_name)
        setattr(mock_blob, "bucket", self)
        return mock_blob

    def list_blobs(self, prefix=None, pattern=None):
        if pattern:
            pattern = pattern.removeprefix(prefix)
        files = list_files(os.path.join(self.mock_bucket, prefix),
                           pattern=pattern, ignore="*.__blobdata__")
        return [self.get_blob(os.path.relpath(file, self.mock_bucket)) for file in files]


class MockClient:
    def __init__(self, project=None, credentials=None):
        self.project = project or "rsc-general-computing"
        self._credentials = credentials

    def get_bucket(self, bucket_or_name):
        return MockBucket(bucket_or_name)

    def bucket(self, bucket_name):
        return MockBucket(bucket_name)

    def list_blobs(self, bucket_or_name, prefix, match_glob=None):
        return self.get_bucket(bucket_or_name).list_blobs(prefix, match_glob)


def test_get_blob():
    urls = [
        "gs://test_bucket/sample_yamls/invoice.yaml",
        "gs://test_bucket/sample_yamls/model.yml",
        "gs://test_bucket/sample_yamls/sample3.yaml",
        "gs://test_bucket/sample_csvs/customers.csv",
        "gs://test_bucket/sample_csvs/income.csv",
    ]
    expected = [
        {
            "bucket": "test_bucket",
            "name": "sample_yamls/invoice.yaml",
            "content_type": "application/x-yaml",
            "size": 547,
            "hashes": {"md5": "eyAkfZtBeaxG/cQFPiDbEg==", "crc32c": "MdRwiQ=="},
            "is_file": True
        },
        {
            "bucket": "test_bucket",
            "name": "sample_yamls/model.yml",
            "content_type": "application/x-yaml",
            "size": 483,
            "hashes": {"md5": "l6BTlxCz4Y2ZfKapM248BQ==", "crc32c": "MF40IQ=="},
            "is_file": True
        },
        {
            "bucket": "test_bucket",
            "name": "sample_yamls/sample3.yaml",
            "content_type": "application/x-yaml",
            "size": 5586,
            "hashes": {"md5": "Bm2PZKSCKZDk5ugeQAdBlA==", "crc32c": "IstUPQ=="},
            "is_file": True
        },
        {
            "bucket": "test_bucket",
            "name": "sample_csvs/customers.csv",
            "content_type": "text/csv",
            "size": 17261,
            "hashes": {"md5": "+SPIdGEdaCS3U1Vi0nYprw==", "crc32c": "rZ4fIQ=="},
            "is_file": True
        },
        {
            "bucket": "test_bucket",
            "name": "sample_csvs/income.csv",
            "content_type": "text/csv",
            "size": 3342,
            "hashes": {"md5": "hd6blmKW/29jeDMj5o2DSw==", "crc32c": "0TZBrA=="},
            "is_file": True
        },
    ]

    with patch("google.cloud.storage.Client.from_service_account_info", return_value=MockClient()):
        for idx, url in enumerate(urls):
            blob = GcsStorage.shared().get_blob(url_string=url)
            exp = expected[idx]
            for key in exp:
                if type(exp[key]) is dict:
                    assert json.dumps(exp[key]) == json.dumps(getattr(blob, key))
                else:
                    assert exp[key] == getattr(blob, key)


def test_list_blobs():
    data = [
        {"url": "gs://test_bucket/sample_yamls/*.yaml", "count": 2},
        {"url": "gs://test_bucket/sample_yamls", "count": 3},
        {"url": "gs://test_bucket/sample_csvs", "count": 2},
        {"url": "gs://test_bucket/*.csv", "count": 2},
    ]

    with patch("google.cloud.storage.Client.from_service_account_info", return_value=MockClient()):
        for item in data:
            blobs = GcsStorage.shared().list_blobs(url=item.get("url"))
            assert len(blobs) == item.get("count")
            for blob in blobs:
                assert type(blob) is GcsBlob
                assert blob.is_file


def test_blob_exists():
    urls = [
        ("gs://test_bucket/sample_yamls/missing.yaml", False),
        ("gs://test_bucket/sample_yamls/model.yml", True),
        ("gs://test_bucket/sample_yamls/invoice.yaml", True),
        ("gs://test_bucket/sample_csvs/customers.csv", True),
        ("gs://test_bucket/sample_csvs/missing.csv", False),
    ]

    with patch("google.cloud.storage.Client.from_service_account_info", return_value=MockClient()):
        for item in urls:
            exists = GcsStorage.shared().blob_exists(url_string=item[0])
            assert exists is item[1]
