from server_core.utils import cast2list
from .content import Content
from .file_content import FileContent
from .gcs_content import GcsContent
from .url_content import UrlContent
from .db_content import DbContent
from .docker_content import DockerContent
from google.cloud.storage.blob import Blob

OBJECT_CONTENTS = {
    "file": FileContent,
    "url": UrlContent,
    "sql": DbContent,
    "gcs": GcsContent,
    "gcr": DockerContent
}
DEFAULT_OBJECT = "file"
SOURCES = {
    "url": ["http", "https", "ftp", "ftps"],
    "gcs": ["gs://"],
    "sql": ["sql:"],
    "gcr": ["gcr.io"]
}


class ContentFactory:

    def de_serialize(self, asset, data: dict):
        cls = self.find_content_class(data)
        return cls.de_serialize(asset=asset, data=data)

    def find_content_class(self, data):
        return self.content_class(recurse(data, "type"))

    def content_class(self, src_type: str) -> Content.__class__:
        if not src_type:
            src_type = DEFAULT_OBJECT
            # raise ValueError("required src_type is missing")
        return OBJECT_CONTENTS[src_type]

    def sort(self, srcs) -> dict:
        targets = cast2list(srcs)
        sorted = {"file": [], "gcs": [], "url": [], "sql": []}
        for src in targets:
            sorted[src_type(src)].append(src)
        return sorted

    def groups(self, contents: [Content]) -> dict:
        groups = {}
        for obj in contents:
            seen = groups.get(obj.file_id, [])
            seen.append(obj)
            groups[obj.unique_repr] = seen
        return groups


def src_type(src):
    if isinstance(src, str):
        for k, v in SOURCES.items():
            for pattern in v:
                if src.startswith(pattern):
                    return k
    elif isinstance(src, Blob):
        return "gcs"
    return "file"


def recurse(d, key):
    for k, v in d.items():
        if isinstance(v, dict):
            return recurse(v, key)
        else:
            if k == key:
                return v
    return None
