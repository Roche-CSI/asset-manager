# models
from server_core.models.base.base import db_proxy as db
from server_core.models.asset import Asset as AssetModel
from server_core.models.content import Content as ContentModel
from server_core.models.object import Object as ObjectModel
from server_core.models.asset_object_relations import AssetObjectRelations
from server_core.models.asset_class_content_relations import AssetClassContentRelations
from server_core.models.asset_class import AssetClass as AssetClassModel
from server_core.models.asset_version import AssetVersion as AssetVersionModel
from server_core.models.version_counter import VersionCounter
from peewee import DoesNotExist
# clients
from .asset import Asset
from .asset_class import AssetClass
from .objects import Object
from .contents import ContentFactory
from .asset_version import AssetVersion
# gcp
from server_core.gcp.async_gcp import write_yaml_to_bucket


class AssetWriter:
    """connector between client Asset and db Asset
    """
    asset: Asset = None

    def __init__(self, asset=None):
        self.asset = asset

    def save_to_db(self, commit_msg=None):
        with db.atomic() as txn:
            asset: Asset = self.asset
            asset_class_record = self.get_asset_class_record(class_id=asset.asset_class.id)
            asset_record = self.get_create_asset_record(asset=asset)

            # todo: check if the commit is same as the leaf version commit in db, in that case,
            #  we don't need to commit again
            # this addresses 2 scenarios,
            # 1: a different user may have added a version in which case the current updates are not necessary
            # 2. the previous commit might have had a network interruption because of which client didnt; receive the
            # commit confirmation

            # 2. Make entries in the contents table
            content_records = self.create_content_records(user=asset.user,
                                                          contents=asset.contents)

            # 3. Make entries in the asset_class_content_relations table
            asset_class_content_joins = self.create_asset_class_content_joins(user=asset.user,
                                                                              class_id=asset_class_record.id,
                                                                              content_records=content_records)

            # 4. Create records in Objects table
            object_records = self.get_create_object_records(user=asset.user,
                                                            objects=asset.objects)

            # 5. Create records in the asset_object relations
            asset_object_joins = self.create_asset_object_joins(user=asset.user,
                                                                asset_id=asset_record.id,
                                                                object_records=object_records)

            # create version
            version = AssetVersionModel.create(user=asset.user,
                                               asset=asset_record,
                                               objects=asset.objects,
                                               commit_hash=asset.objects.hash,
                                               commit_message=commit_msg)

            asset.version.de_serialize(asset=asset, data=version.to_dict(fields=AssetVersion.serialize_fields()))

            asset_record.save(user=asset.user)

            return {
                "asset_class_record": asset_class_record,
                "asset_record": asset_record,
                "version_record": version,
                "content_records": content_records,
                "asset_class_content_relations": asset_class_content_joins,
                "object_records": object_records,
                "asset_object_relations": asset_object_joins
            }

    def write_to_bucket(self, records: dict):
        asset_record: AssetModel = records["asset_record"]
        asset = self.asset
        # sequence id gets assigned to asset_record
        # so we assign to asset, since newly created asset will not have seq_id in the AssetClient object
        asset.seq_id = asset_record.seq_id

        # write asset.yaml
        contents = []
        asset_record: AssetModel = records["asset_record"]
        if asset_record.did_create:
            asset_yaml = {
                "data": asset_record.to_dict(fields=AssetModel.yaml_fields()),
                "url": asset.yaml_url
            }
            contents.append(asset_yaml)

        # write version yaml
        version_yaml = records["version_record"].to_dict(AssetVersionModel.yaml_fields())
        version_yaml["asset"] = str(version_yaml["asset"]["id"])
        version_yaml = {
            "data": version_yaml,
            "url": asset.version.yaml_url
        }
        contents.append(version_yaml)

        # write objects.yaml
        # objects_yaml = {"objects": self.__class__.object_records_to_dict(records["object_records"])}
        objects_yaml = [{
            "data": obj_model.to_dict(recurse=True, fields=ObjectModel.yaml_fields()),
            "url": asset.objects.yaml_url(url_id=obj_model.url_id)
        } for obj_model in records["object_records"]]

        contents += objects_yaml
        write_yaml_to_bucket(contents=contents)

    def get_leaf_asset(self, class_id, seq_id):
        """Return the latest asset belonging to the same asset and with the same sequence id
        We do this to ensure asset versioning is linear
        """
        if not seq_id:
            raise Exception("seq_id can not be null")
        try:
            return AssetModel.select(). \
                where((AssetModel.asset_class == class_id) &
                      (AssetModel.seq_id == seq_id) &
                      AssetModel.commit_hash.is_null(False)). \
                order_by(AssetModel.created_at.desc()).get()
        except DoesNotExist:
            return None

    def get_root_asset(self, class_id, seq_id):
        """Return the latest asset belonging to the same asset and with the same sequence id
                    We do this to ensure asset versioning is linear
                    """
        if not seq_id:
            raise Exception("seq_id can not be null")
        try:
            return AssetModel.select(). \
                where((AssetModel.asset_class == class_id) &
                      (AssetModel.seq_id == seq_id) &
                      AssetModel.commit_hash.is_null(False)). \
                order_by(AssetModel.created_at.asc()).get()
        except DoesNotExist:
            return None

    def get_asset_class_record(self, class_id):
        """Get the asset class record from database"""
        asset_class_record = AssetClassModel.get_if_exists(AssetClassModel.id == class_id,
                                                           include_deleted_records=True)
        # if asset_class doesn't exist, throw error
        if not asset_class_record:
            raise Exception("missing asset_class record, this asset can not be committed")

        # restore if soft deleted previously
        if asset_class_record.status == AssetClassModel.statuses.DELETED:
            # todo: return message to user to undo delete the asset_class, this should be a separate operation
            asset_class_record.restore()

        return asset_class_record

    def get_create_asset_record(self, asset):
        if not asset.id:
            raise Exception("missing asset id")
        # if asset doesn't exist, throw error
        asset_record = AssetModel.get_if_exists(AssetModel.id == asset.id,
                                                include_deleted_records=True)
        if asset_record:
            return asset_record
        return AssetModel.create(user=asset.user,
                                 asset_class=asset.asset_class.id,
                                 id=asset.id)

    def create_content_records(self, user, contents):
        records = []
        for content in contents:
            # reuse of it exists
            record: ContentModel = ContentModel.get_if_exists(ContentModel.id == content.id,
                                                              include_deleted_records=True)
            # create if not exists
            if not record:
                record = ContentModel.create(user=user, **content.serialize())
            # restore if soft deleted previously
            if record.status == record.statuses.DELETED:
                record.restore()  # restore
            records.append(record)

        return records

    def create_asset_class_content_joins(self, user, class_id, content_records):
        relations = []
        for record in content_records:
            join_record = AssetClassContentRelations.get_if_exists(asset_class=class_id,
                                                                   content=record.id,
                                                                   include_deleted_records=True)
            # create if not exists
            if not join_record:
                join_record = AssetClassContentRelations.create(user=user,
                                                                asset_class=class_id,
                                                                content=record.id)
            # if soft deleted, then we restore it
            if join_record.status == join_record.statuses.DELETED:
                join_record.restore()  # restore
            relations.append(join_record)

        return relations

    def get_create_object_records(self, user, objects):
        """create object records if they don't exist already"""
        object_records = []
        for object in objects:
            # if object.url_id:
            #     # url_id gets auto created, so object exists
            #     # and has been tagged to the asset already
            #     continue

            # if there is no url id, we verify if the object exists
            exists = ObjectModel.get_if_exists(ObjectModel.id == object.id,
                                               include_deleted_records=True)
            if not exists:
                data = object.serialize()
                data["content"] = data["content"]["id"]  # we just need the id
                exists = ObjectModel.create(user=user, **data)

            # restore if it was deleted earlier by a user
            if exists.status == ObjectModel.statuses.DELETED:
                exists.restore()

            object_records.append(exists)

        return object_records

    def create_asset_object_joins(self, user, asset_id, object_records):
        relations = []
        for record in object_records:
            relation = AssetObjectRelations.get_if_exists(AssetObjectRelations.asset == asset_id,
                                                          AssetObjectRelations.object == record.id)  # peewee allows id
            if not relation:
                relation = AssetObjectRelations.create(user=user,
                                                       asset=asset_id,
                                                       object=record)
            # restore if soft deleted
            if relation.status == relation.statuses.DELETED:
                relation.restore()

            relations.append(relation)

        return relations

    @classmethod
    def retrieve_from_db(cls, asset_record):
        """create yaml representation of the asset from db"""
        if not isinstance(asset_record, AssetModel):
            # user might have passed id instead of the record, peewee also allows this
            asset_record: AssetModel = AssetModel.get_if_exists(AssetModel.id == asset_record)

        data = asset_record.to_dict(fields=Asset.serialize_fields())
        data["asset_class"] = asset_record.asset_class.to_dict(fields=AssetClass.serialize_fields())
        counter: VersionCounter = asset_record.version_counter.get()
        # add objects
        data["objects"] = cls.get_objects(counter.leaf_objects)
        if counter.leaf_version:
            data["version"] = counter.leaf_version.to_dict(fields=AssetVersion.serialize_fields())

        return data

    @classmethod
    def serialize_records(cls, saved_records):
        """
        Parameters
        ----------
        saved_records:
        {
                "asset_class_record": asset_class_record,
                "asset_record": asset_record,
                "version_record": version,
                "content_records": content_records,
                "asset_class_content_relations": asset_class_content_joins,
                "object_records": object_records,
                "asset_object_relations": asset_object_joins
            }

        Returns
        -------

        """
        asset_record: AssetModel = saved_records["asset_record"]
        asset_data = asset_record.to_dict(fields=Asset.serialize_fields())

        asset_class_record: AssetClassModel = saved_records["asset_class_record"]
        asset_data["asset_class"] = asset_class_record.to_dict(fields=AssetClass.serialize_fields())

        version_record: AssetVersionModel = saved_records["version_record"]
        asset_data["version"] = version_record.to_dict(fields=AssetVersion.serialize_fields())

        object_records: [ObjectModel] = saved_records["object_records"]
        asset_data["objects"] = [cls.object_to_dict(record) for record in object_records]

        return asset_data

    @classmethod
    def get_objects(cls, object_ids):
        """get all objects related to an asset"""
        if not object_ids:
            return []
        data = []
        for obj_id in object_ids:
            obj: ObjectModel = ObjectModel.get_if_exists(ObjectModel.id == obj_id)
            if obj:
                data.append(cls.object_to_dict(obj))
        return data

    @classmethod
    def object_to_dict(cls, obj: ObjectModel):
        data = obj.to_dict(fields=Object.serialize_fields())
        content_class = ContentFactory().find_content_class(obj.content.meta)
        data["content"] = obj.content.to_dict(fields=content_class.serialize_fields())
        return data

    @classmethod
    def object_records_to_dict(cls, records: [ObjectModel]):
        serialized = []
        for record in records:
            data = record.to_dict(fields=Object.serialize_fields())
            content_class = ContentFactory().find_content_class(record.content.meta)
            data["content"] = record.content.to_dict(fields=content_class.serialize_fields())
            serialized.append(data)
        return serialized
