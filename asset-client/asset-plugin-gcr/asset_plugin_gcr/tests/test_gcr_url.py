from asset_plugin_gcr.gcr_url import GcrURL


def test_gcr_urls():
    test_cases = [
        {
            "url": "gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "expected": {
                "host": "gcr.io",
                "project": "my-test-project",
                "image": "my-test-image",
                "hash": "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "tag": None,
                "is_valid": True
            }
        },
        {
            "url": "us.gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "expected": {
                "host": "us.gcr.io",
                "project": "my-test-project",
                "image": "my-test-image",
                "hash": "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "tag": None,
                "is_valid": True
            }
        },
        {
            "url": "gcr.io/my-test-project/my-test-image:latest",
            "expected": {
                "host": "gcr.io",
                "project": "my-test-project",
                "image": "my-test-image",
                "hash": None,
                "tag": "latest",
                "is_valid": True
            }
        },
        {
            "url": "gcr.io/my-test-project/my-test-image",
            "expected": {
                "host": "gcr.io",
                "project": "my-test-project",
                "image": "my-test-image",
                "hash": None,
                "tag": None,
                "is_valid": False
            }
        },
        {
            "url": "gcr.io/my-test-project/my-test-image/",
            "expected": {
                "host": "gcr.io",
                "project": "my-test-project",
                "image": "my-test-image",
                "hash": None,
                "tag": None,
                "is_valid": False
            }
        },
        {
            "url": "gcr.io/my-test-project/",
            "expected": {
                "host": "gcr.io",
                "project": "my-test-project",
                "image": None,
                "hash": None,
                "tag": None,
                "is_valid": False
            }
        },
        {
            "url": "gcr.io/",
            "expected": {
                "host": "gcr.io",
                "project": None,
                "image": None,
                "hash": None,
                "tag": None,
                "is_valid": False
            }
        },
    ]

    for case in test_cases:
        gcr_url = GcrURL(url=case["url"])
        expected = case["expected"]
        assert gcr_url.host == expected["host"]
        assert gcr_url.project == expected["project"]
        assert gcr_url.image == expected["image"]
        assert gcr_url.hash == expected["hash"]
        assert gcr_url.tag == expected["tag"]
        assert gcr_url.is_valid() == expected["is_valid"]
        assert gcr_url.is_remote() == expected["is_valid"]
