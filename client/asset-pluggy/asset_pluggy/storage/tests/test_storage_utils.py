from asset_pluggy.storage.storage_utils import filter_blobs


class MockBlob:
    def __init__(self, name):
        self.name = name


def test_filter_blobs():
    sample_blobs = [MockBlob(name="blob1.txt"),
                    MockBlob(name="ignore_blob.txt"),
                    MockBlob(name="blob2.txt")]

    # without ignore or pattern
    filtered = filter_blobs(blobs=sample_blobs, name_key="name")
    assert len(filtered) == 3, "Should return all blobs when no ignore or pattern is specified"

    # with ignore pattern
    filtered = filter_blobs(blobs=sample_blobs, name_key="name", ignore=["ignore_*"])
    assert len(filtered) == 2, "Should filter out blobs matching the ignore pattern"
    assert all(blob.name != "ignore_blob.txt" for blob in filtered), "Ignored blobs should not be in the result"

    # with match pattern
    filtered = filter_blobs(blobs=sample_blobs, name_key="name", pattern="*.txt")
    assert len(filtered) == 3, "Should return all blobs matching the txt pattern"

    # with ignore and match patterns
    filtered = filter_blobs(blobs=sample_blobs, name_key="name", ignore=["ignore_*"], pattern="*.txt")
    assert len(filtered) == 2, "Should return blobs matching the pattern but not the ignore pattern"
    assert all(blob.name != "ignore_blob.txt" for blob in filtered), "Ignored blobs should not be in the result"
