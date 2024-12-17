from asset_pluggy.storage import StorageURL

HASH_SEPARATOR = "@"
TAG_SEPARATOR = ":"
PATH_SEPARATOR = "/"


class GcrURL(StorageURL):
    host: str = None
    project: str = None
    image: str = None
    hash: str = None
    tag: str = None

    def parse_url(self, url: str) -> None:
        """Parse a gcr url into various components

        e.g. gcr.io/my-test-project/my-test-image@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890
        - host: gcr.io
        - project: my-test-project
        - image: my-test-image
        - hash: sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890

        Parameters
        ----------
        url: str
            The GCR url to parse
        """
        # sanitize by stripping any leading or trailing slashes
        url = url.strip(PATH_SEPARATOR)
        # note: check for HASH_SEPARATOR first, because the TAG_SEPARATOR is also present in the hash-string
        if HASH_SEPARATOR in url:
            image_part, self.hash = url.split(HASH_SEPARATOR)
        elif TAG_SEPARATOR in url:
            image_part, self.tag = url.split(TAG_SEPARATOR)
        else:
            image_part = url
        parts = image_part.split(PATH_SEPARATOR)
        attrs_map = [
            {"name": "host", "index": 0},
            {"name": "project", "index": 1},
            {"name": "image", "index": 2}
        ]
        for attr in attrs_map:
            idx = attr.get("index")
            val = parts[idx] if len(parts) > idx else None
            setattr(self, attr.get("name"), val)

    def is_valid(self):
        if not (self.hash or self.tag):
            return False
        return bool(self.host and self.project and self.image)

    def is_remote(self):
        return self.is_valid()

    def url_for_blob(self, host: str, name: str, hash_type: str, hash_value: str):
        # todo - ":" is a reserved character in linux so we need to fix this
        return f"{host}/{name}{HASH_SEPARATOR}{hash_type}:{hash_value}"
