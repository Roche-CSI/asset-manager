from asset_client.contents import ContentFactory as Factory


def test_sort():
    urls = ["gs://bucket/genomes/dev",
            "/root/dir/file_name",
            "https://stackoverflow.com/questions/61089238",
            "sql: SELECT * FROM host"
            ]
    expected = {
        "file": ["/root/dir/file_name"],
        "gcs": ["gs://bucket/genomes/dev"],
        "url": ["https://stackoverflow.com/questions/61089238"],
        "sql": ["sql: SELECT * FROM host"]
    }
    sorted = Factory().sort(urls)
    assert sorted == expected