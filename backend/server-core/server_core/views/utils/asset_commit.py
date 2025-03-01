import copy

from server_core.models.asset import Asset as AssetModel
from server_core.models.asset_class import AssetClass as AssetClassModel
from server_core.models.asset_class_content_relations import AssetClassContentRelations
from server_core.models.asset_object_relations import AssetObjectRelations
from server_core.models.asset_version import AssetVersion as AssetVersionModel
from server_core.models.base.base import db_proxy as db
from server_core.models.content import Content as ContentModel
from server_core.models.object import Object as ObjectModel
from server_core.views.utils.commit_data import CommitData


class AssetCommit:
    """connector between client Asset and db Asset
    """
    manifest_data: dict = None
    username: str = None

    def __init__(self,
                 data: dict = None,
                 username: str = None):
        self.manifest_data = data
        self.username = username

    def save_to_db(self) -> CommitData:
        cd = CommitData()
        # split data and validate
        class_data, asset_data, version_data, objects_data = self.validate(data=copy.deepcopy(self.manifest_data))
        with db.atomic() as txn:
            # create db entries
            cd.asset_class = self.get_asset_class_record(class_data=class_data)
            cd.asset = self.get_create_asset_record(asset_class=cd.asset_class, asset_data=asset_data)
            cd.content_ids, cd.content_rel_ids = self.create_contents(objects_data=objects_data,
                                                                      asset_class=cd.asset_class)
            cd.object_ids, cd.object_rel_ids = self.create_objects(objects_data=objects_data,
                                                                   asset=cd.asset)
            # create version
            num_objects, data_size = self.calc_version_size()
            cd.version = AssetVersionModel.create(user=self.username,
                                                  asset=cd.asset,
                                                  objects=objects_data,
                                                  commit_hash=version_data.get("commit_hash"),
                                                  commit_message=version_data.get("commit_message"),
                                                  size=version_data.get("size") or data_size,
                                                  num_objects=version_data.get("num_objects") or num_objects
                                                  )
            cd.asset.save(user=self.username)
            return cd

    def calc_version_size(self) -> tuple:
        """Calculate the size of the asset version.
        Returns
        -------
        int
            The size of the asset version.
        """
        objects = self.manifest_data.get("objects", [])
        return len(objects), sum([obj.get("content", {}).get("size", 0) for obj in objects])

    def create_contents(self, objects_data: dict, asset_class: AssetClassModel):
        # 2. Make entries in the contents table
        # first extra contents data
        contents_data = []
        for obj_data in objects_data:
            content = obj_data.pop("content")
            obj_data["content"] = content["id"]  # substitute with id
            obj_data["size"] = content["size"]  # add size
            contents_data.append(content)
        # create content records
        content_ids = ContentModel.batch_insert(user=self.username, data=contents_data)
        # 3. Make entries in the asset_class_content_relations table
        content_rels_data = [{"content": cont_data["id"], "asset_class": asset_class.id} for cont_data in
                             contents_data]
        content_rel_ids = AssetClassContentRelations.batch_insert(user=self.username, data=content_rels_data)

        return content_ids, content_rel_ids

    def create_objects(self, objects_data: list, asset: AssetModel):
        object_ids = ObjectModel.batch_insert(user=self.username, data=objects_data)
        # 5. Create records in the asset_object relations
        # note: we are not using object_ids here because batch-create returns only newly created ids
        # its possible that the object already existed as part of a different asset
        object_rels_data = [{"object": obj_data["id"], "asset": asset.id} for obj_data in objects_data]
        object_rel_ids = AssetObjectRelations.batch_insert(user=self.username, data=object_rels_data)
        return object_ids, object_rel_ids

    def validate(self, data) -> tuple:
        class_data: dict = data.pop("asset_class")
        objects_data: list = data.pop("objects")
        version_data: dict = data.pop("version")
        asset_data: dict = data  # the remaining keys belong to asset

        if not class_data.get("id") or not class_data.get("project"):
            raise Exception("missing required params in class-data: id, project")
        if not objects_data:
            # todo: discuss whether we should allow empty assets
            raise Exception("missing objects")
        if not version_data.get("commit_hash"):
            raise Exception("missing required parameter in version-data: commit_hash")
        if not asset_data.get("id"):
            raise Exception("missing required parameter in asset-data: id")

        return class_data, asset_data, version_data, objects_data

    def get_asset_class_record(self, class_data: dict):
        """Get the asset class record from database"""
        # create asset-class
        asset_class = AssetClassModel.get_if_exists(AssetClassModel.project == str(class_data["project"]),
                                                    AssetClassModel.id == class_data["id"],
                                                    include_deleted_records=True)
        if not asset_class:
            raise Exception("missing asset-class")
        if asset_class.is_deleted:
            raise Exception(f"asset-class:{str(asset_class.id)} is deleted")
        return asset_class

    def get_create_asset_record(self, asset_class: AssetClassModel, asset_data) -> AssetModel:
        asset_record = AssetModel.get_if_exists(AssetModel.id == asset_data.get("id"),
                                                AssetModel.asset_class == asset_class.id,
                                                include_deleted_records=True)
        if not asset_record:
            asset_record = AssetModel.create(user=self.username,
                                             asset_class=asset_class.id,
                                             id=asset_data.get("id"))
        return asset_record