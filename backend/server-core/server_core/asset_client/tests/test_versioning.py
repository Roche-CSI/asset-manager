from asset_client.versioning import increment_version


def test_increment_version():
    data = [(None, "0.0.0"),
            ("0.0.1", "0.0.2"),
            ("1.0.0", "1.0.1"),
            ("1.0.99", "1.1.0"),
            ("1.99.99", "2.0.0"),
            ]
    for case in data:
        actual = increment_version(case[0])
        assert actual == case[1]