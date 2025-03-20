from typing import TYPE_CHECKING
from typing import Type

from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from asset_utils.utils import cast2list
from .blobstore_content import BlobStoreContent
from .content import Content
from .db_content import DbContent
from .docker_content import DockerContent
from .posix_content import PosixContent
from .url_content import UrlContent

if TYPE_CHECKING:
    from google.cloud.storage.blob import Blob

OBJECT_CONTENTS = {
    "file": PosixContent,
    "url": UrlContent,
    "sql": DbContent,
    "gcs": BlobStoreContent,
    "gcr": DockerContent
}
DEFAULT_OBJECT = "file"
SOURCES = {
    "url": ["http", "https", "ftp", "ftps"],
    "gcs": ["gs://"],
    "sql": ["sql:"],
    "gcr": ["gcr.io/", "us.gcr.io/"]
}


class ContentFactory:
    def compute_hash(self, src):
        content_cls: Type[Content] = self.content_class(src_type=src_type(src))
        return content_cls.serialize_hash(*content_cls.compute_hash(src))

    def create(self, asset, **kwargs):
        """
        Parameters
        ----------
        asset: Reference to asset
        kwargs:
            src: string source or gcloud Blob object
        """
        cls = self.content_class(src_type=src_type(kwargs.get("src")))
        return cls.create(asset, **kwargs)

    def create_contents(self, source_data: dict, proxy: bool = False) -> [Content]:
        """Creates Content objects from ObjectSource

        Parameters
        ----------
        source_data:
            {storage_name: [ObjectSource]}
        proxy: bool
            if true, creates proxy content

        Returns
        -------
        [Content]
        """
        result = []
        for storage_name, object_sources in source_data.items():
            storage_klass: Type[AssetStorage] = StorageFactory.storage_with_name(name=storage_name)
            content_klass: Type[Content] = storage_klass.get_content_class()
            for object_src in object_sources:
                object_src.content = content_klass.create(storage_name=storage_name,
                                                          blob=object_src.blob,
                                                          proxy=proxy)
                result.append(object_src)
        return result

    def de_serialize(self, asset, data: dict):
        cls = self.content_class(recurse(data, "type"))
        return cls.de_serialize(asset=asset, data=data)

    def content_class(self, src_type: str) -> Type[Content]:
        if not src_type:
            src_type = DEFAULT_OBJECT
        # legacy fix, the type in older projects is "gcs" - this is now changed to "gs"
        if src_type == "gcs":
            src_type = "gs"
        if src_type == "aws_s3":
            src_type = "s3"
        storage_klass: AssetStorage = StorageFactory.storage_with_name(name=src_type)
        return storage_klass.get_content_class()

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
    elif isinstance(src, dict):
        src = src.get("src") or "gcr"
        for k, v in SOURCES.items():
            for pattern in v:
                if src.startswith(pattern):
                    return k
    return "file"


def recurse(d, key):
    for k, v in d.items():
        if isinstance(v, dict):
            return recurse(v, key)
        else:
            if k == key:
                return v
    return None
