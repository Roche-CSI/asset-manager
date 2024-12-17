from unittest.mock import patch

from asset_contents import Content


def test_proxy_hash():
    test_items = [
        {
            "source": "gs://test_bucket/user_testing/test/file_1.txt",
            "content_hash": "md5_l6BTlxCz4Y2ZfKapM248BQ==",
            "proxy_hash": "md5_tkJI23EYs+rF4K1ZsyMnyQ=="
        },
        {
            "source": "s3://test_bucket/user_testing/test/file_2.txt",
            "content_hash": 'etag_"7b20247d9b4179ac46fdc4053e20db12"',
            "proxy_hash": "md5_6CR0xOHHr6H2u4zjNoHAgA=="
        },
    ]

    for item in test_items:
        got_hash = Content.proxy_hash(item.get("source"), item.get("content_hash"))
        assert got_hash == item.get("proxy_hash")


def test_compute_id():
    test_items = [
        {
            'hash': 'md5_l6BTlxCz4Y2ZfKapM248BQ==',
            'storage_name': 'posix',
            'expected_id': 'gs:md5_l6BTlxCz4Y2ZfKapM248BQ=='
        },
        {
            'hash': 'md5_l6BTlxCz4Y2ZfKapM248BQ==',
            'meta': {'proxy': True,
                     'src': 'gs://test_bucket/user_testing/test/file_1.txt',
                     'type': 'gs'},
            'storage_name': 'gs',
            'expected_id': 'gs:proxy_md5_tkJI23EYs+rF4K1ZsyMnyQ=='
        },
        {
            'hash': 'etag_"7b20247d9b4179ac46fdc4053e20db12"',
            'meta': {'proxy': True,
                     'src': 's3://test_bucket/user_testing/test/file_2.txt',
                     'type': 's3'},
            'storage_name': 's3',
            'expected_id': 's3:proxy_md5_6CR0xOHHr6H2u4zjNoHAgA=='
        },
    ]

    for item in test_items:
        with patch.object(Content, 'storage_system_id', return_value='gs'):
            got_id = Content.compute_id(hash=item.get("hash"),
                                        meta=item.get("meta"),
                                        storage_name=item.get("storage_name"))
        assert got_id == item.get("expected_id")
