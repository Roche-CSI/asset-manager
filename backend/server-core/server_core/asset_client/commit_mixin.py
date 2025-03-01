from server_core.configs import Configs
from .asset_object import AssetObject
from server_core.gcp import list_url_blobs
# from server_core.gcp.async_gcp import move_from_staging
import os


# noinspection PyAttributeOutsideInit
class CommitMixin:
    """CommitMixin for Node Model,
    handle the commit flow here
    """
    asset_objects = {}

    @property
    def staging_url(self):
        return os.path.join(Configs.shared().objects_url(staging=True), self.asset_class.id_string, self.top_hash)

    @property
    def objects_url(self):
        return os.path.join(Configs.shared().objects_url(staging=False), self.asset_class.id_string, self.top_hash)

    @property
    def url_path(self):
        return os.path.join(self.asset_class.id_string, str(self.seq_id), f"{self.version}.yaml")

    @property
    def url(self):
        return os.path.join(Configs.shared().assets_url, self.url_path)

    def de_serialize(self):
        for id in self.objects:
            self.asset_objects[id] = AssetObject(**{"id": id, **self.objects[id]})

    def commit(self, **kwargs):
        """commits / recommits the node
        1. update the objects
        2. deserialize asset_objects
        2. copy asset_objects from staging to repo url
        3. after objects are transferred, update commit_hash
        Returns
        -------
        """
        # update the objects, store only for the root asset node
        self.objects = {} if self.parent_version else kwargs.get("objects")
        # for leaf nodes i.e. versions, we store only the patch
        self.patch = kwargs.get("patch") if self.parent_version else {}
        # convert objects into Asset_objects
        self.de_serialize()
        # move assets from staging
        # self.move_from_staging()  # todo: uncomment this
        # after the move is complete, we can update the commit_hash
        self.top_hash = kwargs.get("top_hash")
        self.save()

    def move_from_staging(self, objects):
        """transfer assets from staging to remote_url
        """
        not_in_remote = self.objects_not_in_remote(objects)
        # move_from_staging(not_in_remote)

    def objects_not_in_remote(self, objects: [AssetObject]) -> list:
        """Verifies if any of the objects are already in remote or in staging
        Parameters:
            objects: List of AssetObject
        """
        if not objects:
            return []
        # fetch the full list so we can avoid multiple network calls
        # combine assets in remote and in staging
        all_remote_objects = set(
            list_url_blobs(self.objects_url, names_only=True)
        )
        remote_objs, local_objs = [], []
        for obj in objects:
            (remote_objs if obj.id in all_remote_objects else local_objs).append(obj)
        return local_objs