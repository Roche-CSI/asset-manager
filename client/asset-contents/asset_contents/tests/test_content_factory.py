from asset_contents.content_factory import ContentFactory


def test_sort():
    urls = ["gs://test_bucket/mydata/dev",
            "/root/dir/file_name",
            "https://stackoverflow.com/questions/1234567890",
            "sql: SELECT * FROM host"]

    expected = {
        "file": ["/root/dir/file_name"],
        "gcs": ["gs://test_bucket/mydata/dev"],
        "url": ["https://stackoverflow.com/questions/1234567890"],
        "sql": ["sql: SELECT * FROM host"]
    }

    assert ContentFactory().sort(urls) == expected
