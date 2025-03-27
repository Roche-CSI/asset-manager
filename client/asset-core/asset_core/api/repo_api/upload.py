import os

from asset_core.asset import Asset
from asset_core.asset.asset_snapshot import AssetSnapshot
from asset_core.asset.asset_uploader import AssetUploader
from asset_core.objects.asset_object import ObjectViews
from asset_utils.common import exceptions, user_commands
from asset_utils.utils.cloud_utils import internet_on
from .repo import RepoAPI


class UploadAPI(RepoAPI):

    def __init__(self, repo):
        super().__init__(repo=repo)
        self.view = Asset.views.RAW  # upload in raw mode always

    def get_asset(self, view: ObjectViews) -> Asset:
        return Asset(self.repo, view=view) if self.repo else None

    def can_upload(self):
        try:
            return AssetUploader(self.asset).can_upload()
        except exceptions.InvalidCredentialError as e:
            e.logs.add("missing project credentials", e.log_colors.ERROR)
            e.logs.add(user_commands.UserCommands().set_auth())
            raise

    def sync_to_remote(self, commit_msg: str):
        try:
            # upload happens in two stages
            # we first upload the contents in data mode, then we upload the asset in raw mode
            uploaded = AssetUploader(self.asset).upload_asset(commit_msg=commit_msg)
            if uploaded:
                self.user_log.info(message=f"uploaded:{len(uploaded)} objects")
        except exceptions.InvalidCredentialError as e:
            e.logs.add("missing project credentials", e.log_colors.ERROR)
            e.logs.add(user_commands.UserCommands().set_auth())
            raise
        except exceptions.ServerNotAvailableError as e:
            # connection error, we need to check if internet or server
            if not internet_on():
                message = "Unable to connect, make sure you are connected to internet"
            else:
                message = "Asset Server not available. You need to be connected to Roche VPN to upload assets."
            e.logs.add(message, e.log_colors.ERROR)
            raise

        # check if a snapshot needs to be created
        self._upload_snapshot(asset=self.asset)

    def _upload_snapshot(self, asset: Asset):
        """Create and upload the snapshot file for the asset if necessary."""
        if AssetSnapshot.is_snapshot_version(asset.version.number) and not os.path.exists(asset.snapshot_file):
            asset_snapshot = AssetSnapshot(store=self.store)
            asset_snapshot.create_from_manifest(manifest_file=asset.cached_manifest_file)
            asset_snapshot.upload(class_id=asset.asset_class.id,
                                  seq_id=str(asset.seq_id),
                                  version=asset.version.number)
