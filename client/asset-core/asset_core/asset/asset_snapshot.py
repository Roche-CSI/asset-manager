import os

from packaging.version import Version

from asset_core.store import AssetStore
from asset_pluggy.storage import StorageData
from asset_pluggy.storage.storage_factory import StorageFactory
from asset_utils.common import exceptions
from asset_utils.utils import files_at_location
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import LoggingMixin

SNAPSHOT_FILE = "{version}.json"
SNAPSHOTS_DIR = "objects_snapshots"
ASSET_SNAPSHOT_ACTIVE = True


class AssetSnapshot(LoggingMixin):

    def __init__(self, store=None):
        self.store = store or AssetStore.shared()

    def remote_snapshots(self, class_id: str, seq_id: str) -> list:
        """Get the list of all snapshot version numbers from the cloud storage."""
        url = os.path.join(self.remote_dir_url(class_id, seq_id), SNAPSHOT_FILE.format(version="*"))
        storage = StorageFactory.storage_for_url(url)
        blobs = storage.list_blobs(url)
        snapshot_files = [blob.path_in_asset for blob in blobs]
        snapshot_versions = [os.path.splitext(file)[0] for file in snapshot_files]
        return snapshot_versions

    def cached_snapshots(self, class_id: str, seq_id: str) -> list:
        """Get the list of all snapshot version numbers from asset store."""
        snapshots_dir = self.cached_dir(class_id, seq_id)
        snapshot_files = [os.path.basename(file) for file in files_at_location(snapshots_dir)]
        snapshot_versions = [os.path.splitext(file)[0] for file in snapshot_files]
        return snapshot_versions

    def latest_remote_snapshot(self, class_id: str, seq_id: str, version: str = None):
        """Get the latest snapshot version from the cloud."""
        snapshot_versions = self.remote_snapshots(class_id, seq_id)
        return self.latest_snapshot_version(snapshot_versions, version)

    def latest_cached_snapshot(self, class_id: str, seq_id: str, version: str = None):
        """Get the latest snapshot version from the store."""
        snapshot_versions = self.cached_snapshots(class_id, seq_id)
        return self.latest_snapshot_version(snapshot_versions, version)

    def latest_snapshot_version(self, snapshot_versions: list, version: str = None):
        """Get the latest snapshot version number from the list."""
        if version:
            # filter out snapshots higher than the specified version
            snapshot_versions = [snapshot for snapshot in snapshot_versions if Version(snapshot) <= Version(version)]

        if not snapshot_versions:
            # no snapshots found
            return None

        # sort by version number and return the latest
        snapshot_versions.sort(key=Version)
        return snapshot_versions[-1]

    def download(self, class_id: str, seq_id: str, version: str, force=False) -> None:
        """Download the snapshot file from the cloud storage to the store."""
        filename = SNAPSHOT_FILE.format(version=version)
        file_url = os.path.join(self.remote_dir_url(class_id, seq_id), filename)
        cached_file = os.path.join(self.cached_dir(class_id, seq_id), filename)
        # no need to download if the file is already available
        if not force and os.path.exists(cached_file):
            self.user_log.info(f"snapshot already exists for version: {version} - skipping download")
            return

        # check if the snapshot file exists in the cloud storage
        storage = StorageFactory.storage_for_url(file_url)
        blob = storage.get_blob(file_url)
        if not blob:
            raise exceptions.AssetSnapshotError(f"snapshot file not found: {file_url}")

        # download the snapshot file
        transporter = storage.get_transporter()
        resource = transporter.get_download_resource(src=file_url,
                                                     dst=cached_file,
                                                     src_hash=blob.get_hash())
        transporter.download(resources=[resource])
        self.user_log.message(f"downloaded snapshot file for version: {version}")

    def upload(self, class_id: str, seq_id: str, version: str, force=False):
        """Upload the snapshot file from the store to the cloud storage."""
        filename = SNAPSHOT_FILE.format(version=version)
        file_url = os.path.join(self.remote_dir_url(class_id, seq_id), filename)
        cached_file = os.path.join(self.cached_dir(class_id, seq_id), filename)
        if not os.path.exists(cached_file):
            raise exceptions.AssetSnapshotError(f"snapshot file not found: {cached_file}")

        storage = StorageFactory.storage_for_url(file_url)
        # no need to upload if the file is already available
        if not force and storage.blob_exists(file_url):
            self.user_log.info(f"snapshot already exists for version: {version} - skipping upload")
            return None

        # upload the snapshot file
        transporter = storage.get_transporter()
        resource = transporter.get_upload_resource(src=cached_file,
                                                   dst=file_url,
                                                   src_hash=tuple())
        transporter.upload(resources=[resource])
        self.user_log.message(f"uploaded snapshot file for version: {version}")

    def remote_dir_url(self, class_id: str, seq_id: str) -> str:
        """Get the remote directory url for the snapshots."""
        return os.path.join(self.store.asset_url(class_id, seq_id), SNAPSHOTS_DIR)

    def cached_dir(self, class_id: str, seq_id: str) -> str:
        """Get the cached directory for the snapshots."""
        return os.path.join(self.store.asset_cache(class_id, seq_id), SNAPSHOTS_DIR)

    def object_ids(self, class_id: str, seq_id: str, version: str) -> list:
        """Get the list of object ids from the snapshot file."""
        snapshot_file = os.path.join(self.cached_dir(class_id, seq_id), SNAPSHOT_FILE.format(version=version))
        snapshot_data = FileUtils.read_json(snapshot_file)
        return snapshot_data.get("object_ids", [])

    def create_from_manifest(self, manifest_file: str, force=False):
        """Create a snapshot file from the manifest file."""
        manifest_data = FileUtils.read_json(manifest_file)
        class_id = manifest_data.get("asset_class").get("id")
        seq_id = manifest_data.get("seq_id")
        version = manifest_data.get("version").get("number")
        snapshot_file = os.path.join(self.cached_dir(class_id, seq_id), SNAPSHOT_FILE.format(version=version))
        if not force and os.path.exists(snapshot_file):
            self.user_log.info(f"snapshot already exists for version: {version}")
            return snapshot_file

        # create the snapshot file
        object_ids = [obj.get("id") for obj in manifest_data.get("objects", [])]
        snapshot_data = {"object_ids": object_ids}
        FileUtils.write_json(data=snapshot_data, abs_path=snapshot_file)
        return snapshot_file

    @classmethod
    def is_snapshot_version(cls, version: str) -> bool:
        """Check if the version should be a snapshot.

        We only create snapshots for every 50th version.
        """
        if not ASSET_SNAPSHOT_ACTIVE:
            return False

        if version == "0.0.0":
            return False

        return version.endswith(".0") or version.endswith(".50")

    def blob_version(self, blob: StorageData) -> str:
        """Get the version number from the blob path."""
        blob_name = os.path.basename(blob.name).split("_")[1]
        return os.path.splitext(blob_name)[0]

    def filter_version_blobs(self, blobs: list,
                             snapshot_version: str,
                             target_version: str) -> list:
        """Filter the blobs based on the snapshot version and target version."""
        if snapshot_version:
            snapshot_version = Version(snapshot_version)
            blobs = [blob for blob in blobs if Version(self.blob_version(blob)) >= snapshot_version]

        if target_version:
            target_version = Version(target_version)
            blobs = [blob for blob in blobs if Version(self.blob_version(blob)) <= target_version]

        return blobs
