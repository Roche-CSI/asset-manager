from asset_pluggy.storage.storage_factory import StorageFactory
from asset_pluggy.storage.transporter import Transporter
from asset_utils.utils.in_memory_file import InMemoryFile

from server_core import models
from server_core.utils import time_it


class CommitData:
    asset_class: models.AssetClass
    asset: models.Asset
    version: models.AssetVersion
    content_ids: [str]
    content_rel_ids: [str]  # asset_class_content_relations
    object_ids: [str]
    object_rel_ids: [str]  # asset_object_relations

    def __init__(self,
                 asset_cls=None,
                 asset=None,
                 version=None,
                 content_ids=None,
                 content_rels=None,
                 object_ids=None,
                 object_rels=None):

        self.asset_class = asset_cls
        self.asset = asset
        self.version = version
        self.content_ids = content_ids or []
        self.content_rel_ids = content_rels or []
        self.object_ids = object_ids or []
        self.object_rel_ids = object_rels or []

    @property
    def json_data(self) -> dict:
        return self._json_data

    @property
    def bucket_data(self) -> list:
        return self._bucket_data

    def serialize(self):
        asset_data = self.asset.to_dict()
        version_data = self.version.to_dict()
        json_data = {**asset_data, "asset_class": self.asset_class.to_dict(), "version": version_data}

        bucket_data = []
        if self.asset.did_create:
            asset_yaml = {"file": InMemoryFile(file_ext=".yaml", file_data=asset_data),
                          "url": self.asset.yaml_url}
            bucket_data.append(asset_yaml)  # update bucket data also
        version_yaml = {"file": InMemoryFile(file_ext=".yaml", file_data=json_data["version"]),
                        "url": self.version.yaml_url}
        bucket_data.append(version_yaml)

        # new-linked-objects
        objects_data = self.collect_objects()
        objects_yaml = {
            "file": InMemoryFile(file_ext=".zip", file_data={"objects.json": objects_data}),
            "url": models.Object.objects_url(asset_url=self.asset.remote_url,
                                             version=self.version.number,
                                             commit_hash=self.version.commit_hash),
        }
        bucket_data.append(objects_yaml)

        self._bucket_data = bucket_data
        self._json_data = json_data

    def collect_objects(self) -> list:
        """collect bucket-unsaved records from database
        Note:
            - The standard to_dict after join-query is very slow > takes around 3 - 4 minutes
            - So we use an optimized querying approach here
        https://github.com/coleifer/peewee/issues/1177
        Returns
        -------

        """
        # object_rels = models.AssetObjectRelations.batch_read(ids=self.object_rel_ids)
        # note we fetch all records that have not been saved to bucket yet, this has the following benefits
        #  - all write errors to bucket get fixed in the next commit automatically
        #  - deduplication of data in bucket
        #  - auto-migration to v2 schema, because in the bucket an asset will be either in v1 schema or v2 schema
        object_rels = models.AssetObjectRelations.get_objects_not_saved_to_bucket(asset_id=self.asset.id)
        if not object_rels:
            return []
        objects_data = models.Object.batch_read(ids=list(map(lambda x: x.get("object"), object_rels)))
        self.object_rel_ids = list(map(lambda x: x["id"], object_rels))
        return objects_data

    def write_to_bucket(self, storage_url: str):
        """Writes data in yaml format to bucket
        """
        storage = StorageFactory.storage_for_url(src_url=storage_url)
        transporter: Transporter = storage.get_transporter()
        transporter.write_to_bucket(data=self.bucket_data)

    # def write_to_bucket(self, storage_url: str, data: dict = None):
    #     """Writes data in yaml format to bucket
    #
    #     Parameters
    #     ----------
    #     storage_url
    #     data
    #
    #     Returns
    #     -------
    #
    #     """
    #     with tempfile.TemporaryDirectory() as temp_dir:
    #         resources = []
    #         for value in data:
    #             dst = value["url"]
    #             file_name = os.path.basename(dst)
    #             _, ext = os.path.splitext(file_name)
    #             path = os.path.join(temp_dir, file_name)
    #             if ext in ".yaml":
    #                 FileUtils.write_yaml(abs_path=path, data=value["data"])
    #             elif ext == ".json":
    #                 FileUtils.write_json(abs_path=path, data=value["data"])
    #             elif ext == ".zip":
    #                 zip_info = value["data"][0]
    #                 _, info_ext = os.path.splitext(zip_info)
    #                 if info_ext == ".json":
    #                     zip_data = FileUtils.json_serialize(data=value["data"][1])
    #                 elif info_ext == ".yaml":
    #                     zip_data = FileUtils.yaml_serialize(data=value["data"][1])
    #                 else:
    #                     raise Exception("unsupported file format")
    #                 FileUtils.generate_zip(files=[(zip_info, zip_data)], dest=path)
    #             resources.append(TransportResource(src=path, dst=value["url"]))
    #
    #         for res in resources:
    #             print(res.dst)
    #         storage = StorageFactory.storage_for_url(src_url=storage_url)
    #         transporter: Transporter = storage.get_transporter()
    #         transporter.upload(resources=resources)

    def update_object_rels(self):
        with time_it("updating object_rels"):
            models.AssetObjectRelations.update_saved_to_bucket(record_ids=self.object_rel_ids, value=True)
