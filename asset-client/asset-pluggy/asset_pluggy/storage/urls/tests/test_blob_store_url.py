from asset_pluggy.storage.urls import BlobStoreURL


def test_blob_store_url():
    urls = [
        "gs://bucket/test/client/sample_yamls/annotate_params.yaml",
        "s3://bucket/rtd/models/",
        "s3://bucket/rtd/models",
        "gs://",
        "s3://",
        "gs://bucket/",
        "s3://bucket/",
        "gs://bucket",
        "s3://bucket",
        # test with patterns
        "gs://bucket/test/client/sample_yamls/*.yaml",
        "gs://bucket/test/client/*/*.yaml"
    ]
    expected = [
        ("gs", "bucket", "test/client/sample_yamls/annotate_params.yaml", "test/client/sample_yamls", None),
        ("s3", "bucket", "rtd/models/", "rtd/models", None),
        ("s3", "bucket", "rtd/models", "rtd", None),
        ("gs", None, None, None, None),
        ("s3", None, None, None, None),
        ("gs", "bucket", None, None, None),
        ("s3", "bucket", None, None, None),
        ("gs", "bucket", None, None, None),
        ("s3", "bucket", None, None, None),
        ("gs", "bucket", "test/client/sample_yamls/", "test/client/sample_yamls", "test/client/sample_yamls/*.yaml"),
        ("gs", "bucket", "test/client/", "test/client", "test/client/*/*.yaml"),
    ]

    for idx, url in enumerate(urls):
        blob_url = BlobStoreURL(url=url)
        exp = expected[idx]
        assert blob_url.url == url
        assert blob_url.host == exp[0]
        assert blob_url.bucket == exp[1]
        assert blob_url.path == exp[2]
        print(blob_url.__dict__)
        assert blob_url.dir_name == exp[3]
