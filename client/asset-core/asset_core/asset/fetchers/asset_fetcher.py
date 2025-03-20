import os
import tempfile
from typing import Iterable, List

from packaging.version import Version

from asset_contents import Content
from asset_core.asset import Asset
from asset_core.asset.asset_class import AssetClass
from asset_core.asset.asset_snapshot import AssetSnapshot
from asset_core.asset.fetchers.fetcher import Fetcher
from asset_core.objects.asset_object import AssetObject
from asset_pluggy.storage import TransportResource, StorageData
from asset_pluggy.storage.storage_credentials import StorageCredentials
from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from asset_utils.common import exceptions
from asset_utils.utils import list_files, LogColors
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.progress import Progress

ALIAS_YAML_FILE_NAME_FORMAT = "{id}__{seq_id}__{alias}.yaml"
VERSION_YAML_FILE_NAME_FORMAT = "version_{ver_number}.yaml"
OBJECTS_DIR_NAME = "objects_v2"


class AssetFetcher(Fetcher):

    def verify_asset_exists(self, class_id: str, seq_id: str, version=None) -> bool:
        """Check if the asset exists in the bucket.

        Parameters
        ----------
        class_id : str
            The class id of the asset.
        seq_id : str
            The seq id of the asset.
        version : str
            The version of the asset.

        Returns
        -------
        bool
            True if the asset exists, False otherwise.
        """
        asset_url = self.store.asset_url(class_id, seq_id)
        asset_url = os.path.join(asset_url, f"version_{version or '0.0.0'}.yaml")
        storage = StorageFactory.storage_for_url(src_url=asset_url)
        return storage.blob_exists(url_string=asset_url)

    def get_seq_id_from_bucket(self, class_id: str, alias: str):
        """Find the asset seq_id from the bucket using the alias.

        Parameters
        ----------
        class_id : str
            The class id of the asset.
        alias : str
            The alias of the asset.

        Raises
        ------
        exceptions.InvalidAliasError
            If the class id or alias is not provided. Or incorrect alias is found in the bucket.

        Returns
        -------
        seq_id : str
            The seq_id of the asset.
        """
        if not class_id or not alias:
            raise exceptions.InvalidAliasError("class id or alias not provided")

        alias_dir_url = self.store.aliases_url(class_id=class_id)
        blob_name = ALIAS_YAML_FILE_NAME_FORMAT.format(id="*", seq_id="*", alias=alias)
        alias_file_url = os.path.join(alias_dir_url, blob_name)
        storage = StorageFactory.storage_for_url(src_url=alias_dir_url)
        blobs = storage.list_blobs(url=alias_file_url)
        if len(blobs) == 0:
            return None
        # there should never be more than 1 alias
        if len(blobs) > 2:
            raise exceptions.InvalidAliasError(f"multiple aliases found for {alias}")

        blob = blobs[0]
        if alias not in blob.name:
            raise exceptions.InvalidAliasError(f"alias:{alias} not found in bucket, found:{blob.name}")
        # parse the seq_id and alias from the blob name
        parts = os.path.basename(blob.name).split("__")
        alias_in_bucket = "__".join(parts[2:]).removesuffix(".yaml")
        if alias != alias_in_bucket:
            raise exceptions.InvalidAliasError(f"alias:{alias} not found in bucket, found:{alias_in_bucket}")

        return parts[1]

    def get_version_from_bucket(self, class_id: str = None,
                                seq_id: str = None,
                                ver_number: str = None) -> dict:
        """Find the version of the asset from the bucket.
        if ver_number is not provided, then return the latest version.
        """
        if not class_id and not seq_id:
            raise exceptions.AssetException("invalid asset details provided")

        def get_version_blob(blobs_list: list, version: str):
            if version:
                for blob in blobs_list:
                    blob_version = ".".join(os.path.basename(blob.name).split('_')[1].split('.')[:-1])
                    if blob_version == ver_number:
                        return blob
                raise exceptions.InvalidVersionError(f"version:{ver_number} not found in bucket")
            else:
                # return latest
                return \
                    sorted(blobs_list,
                           key=lambda x: list(map(int, os.path.basename(x.name).split('_')[1].split('.')[:-1])),
                           reverse=True)[0]

        def read_blob(blob: StorageData, asset_storage: AssetStorage):
            transporter = asset_storage.get_transporter()
            # download to temp dir so we can read it
            # TODO: we can avoid this by reading the content directly from the blob
            with tempfile.TemporaryDirectory() as temp_dir:
                target = os.path.join(temp_dir, os.path.basename(blob.name))
                resource = transporter.get_download_resource(src=blob.url,
                                                             dst=target,
                                                             src_hash=blob.get_hash())
                transporter.download(resources=[resource])
                # check if the file was downloaded before reading
                if not os.path.exists(target):
                    raise exceptions.AssetException(f"failed to download file: {os.path.basename(target)}")
                return FileUtils.read_yaml(target)

        version_data = None
        # if user didn't pass a version number, we skip local cache check and
        # always check in bucket, since there might be newer versions there
        if class_id and seq_id and ver_number:
            # if user passed a ver_number, check in local cache first, it might have been fetched already
            asset_cache = self.store.asset_cache(class_id=class_id, seq_id=seq_id)
            version_files = list_files(root_dir=asset_cache,
                                       pattern=f"version_{ver_number}.yaml")
            if version_files:
                if len(version_files) > 1:
                    raise exceptions.InvalidVersionError(f"multiple versions found for asset: {ver_number}")
                else:
                    self.user_log.message(f"found version: {ver_number} in local cache, skipping bucket check")
                    version_data = FileUtils.read_yaml(version_files[0])

        if not version_data:
            asset_url = self.store.asset_url(class_id, seq_id)

            # list all version blobs in the asset directory
            blob_name = VERSION_YAML_FILE_NAME_FORMAT.format(ver_number=ver_number or "*")
            storage = StorageFactory.storage_for_url(src_url=asset_url)
            version_urls = os.path.join(asset_url, blob_name)
            blobs: [StorageData] = storage.list_blobs(url=version_urls)
            if len(blobs) == 0:
                raise exceptions.InvalidVersionError(f"no versions found for asset:{seq_id}")

            version_blob = get_version_blob(blobs, ver_number)
            if not version_blob:
                raise exceptions.InvalidVersionError(f"version: {ver_number} not found in bucket")
            version_data = read_blob(version_blob, storage)

        return version_data

    def download_asset(self, asset_name, show_progress=False, force=False):
        class_name, seq_id = Asset.parse_name(asset_name)
        class_id = self.get_asset_class_id(class_name)
        # download class file if not available
        self.download_asset_class(class_id=class_id)
        asset_url = self.store.asset_url(class_id=class_id, seq_id=seq_id)
        asset_cache = self.store.asset_cache(class_id=class_id, seq_id=seq_id)
        self.download_dir(dir_url=asset_url,
                          dir_dst=asset_cache,
                          progress="downloading asset metadata" if show_progress else None,
                          force=force)
        # update assets list
        asset_list = self.create_asset_list_for_class(AssetClass.get_asset_class(store=self.store,
                                                                                 name=class_name))
        return asset_cache, asset_list

    def download_asset_objects(self, class_id, seq_id, show_progress=False, force=False):
        """Download the objects directory of the asset into the store."""
        objects_url = os.path.join(self.store.asset_url(class_id, seq_id), OBJECTS_DIR_NAME)
        objects_cache = os.path.join(self.store.asset_cache(class_id, seq_id), OBJECTS_DIR_NAME)
        self.download_dir(dir_url=objects_url,
                          dir_dst=objects_cache,
                          progress="downloading asset objects" if show_progress else None,
                          force=force)
        return objects_cache

    def download_window_versions(self, class_id: str,
                                 seq_id: str,
                                 target_version: str,
                                 window_size: int = None,
                                 force=False) -> None:
        """Download the window versions of the asset into the store."""

        def _blob_version(item: StorageData) -> Version:
            """Get the Version object from the blob path."""
            blob_name = os.path.basename(item.name).split("_")[1]
            version_number = os.path.splitext(blob_name)[0]
            return Version(version_number)

        asset_url = self.store.asset_url(class_id, seq_id)
        storage = StorageFactory.storage_for_url(src_url=asset_url)
        # get all the available versions of the asset
        version_pattern = VERSION_YAML_FILE_NAME_FORMAT.format(ver_number="*")
        version_blobs = storage.list_blobs(url=os.path.join(asset_url, version_pattern))

        if window_size and len(version_blobs) > window_size:
            # first sort the versions based on the version number
            version_blobs = sorted(version_blobs, key=_blob_version)
            # filter the versions based on the target version and the window size
            target_version = Version(target_version)
            target_index = next((i for i, item in enumerate(version_blobs) if _blob_version(item) == target_version),
                                None)
            if target_index is None:
                raise exceptions.InvalidVersionError(f"target version: {target_version} not found in bucket")

            # calculate the start and end indices for the window
            half_window = window_size // 2
            start_index = max(0, target_index - half_window)
            end_index = start_index + window_size

            # adjust start and end indices if end index exceeds the list length
            if end_index > len(version_blobs):
                end_index = len(version_blobs)
                start_index = max(0, end_index - window_size)

            # filter the blobs based on the window
            version_blobs = version_blobs[start_index:end_index]

        transporter = storage.get_transporter()
        # create a list of resources to download the version files
        target_resources = []
        asset_cache_dir = self.store.asset_cache(class_id, seq_id)
        for blob in version_blobs:
            version_file = os.path.join(asset_cache_dir, blob.path_in_asset)
            if force or not os.path.exists(version_file):
                resource = transporter.get_download_resource(src=blob.url,
                                                             dst=version_file,
                                                             src_hash=blob.get_hash())
                target_resources.append(resource)

        if not target_resources:
            self.user_log.info("all necessary version files are available - skipping download")
            return

        self.perform_download(targets=target_resources,
                              storage=storage,
                              progress="downloading asset versions")

    def download_snapshot_versions(self, class_id: str,
                                   seq_id: str,
                                   snapshot_version: str,
                                   target_version: str,
                                   force=False) -> None:
        """Download the necessary version_*.yaml files of the asset into the store.
        - use the latest version if target_version is not provided
        - filter the versions based on the snapshot version
        - only versions greater than snapshot_version up to target_version are needed
        - no need to download if the version file is already available
        """
        asset_url = self.store.asset_url(class_id, seq_id)
        storage = StorageFactory.storage_for_url(src_url=asset_url)
        # get all the available versions of the asset
        version_pattern = VERSION_YAML_FILE_NAME_FORMAT.format(ver_number="*")
        version_blobs = storage.list_blobs(url=os.path.join(asset_url, version_pattern))
        # filter the blobs based on the snapshot and the target version
        asset_snapshot = AssetSnapshot(store=self.store)
        filtered_blobs = asset_snapshot.filter_version_blobs(blobs=version_blobs,
                                                             snapshot_version=snapshot_version,
                                                             target_version=target_version)
        transporter = storage.get_transporter()
        # create a list of resources to download the version files
        target_resources = []
        asset_cache_dir = self.store.asset_cache(class_id, seq_id)
        for blob in filtered_blobs:
            version_file = os.path.join(asset_cache_dir, blob.path_in_asset)
            if force or not os.path.exists(version_file):
                resource = transporter.get_download_resource(src=blob.url,
                                                             dst=version_file,
                                                             src_hash=blob.get_hash())
                target_resources.append(resource)

        if not target_resources:
            self.user_log.info("all necessary version files are available - skipping download")
            return

        self.perform_download(targets=target_resources,
                              storage=storage,
                              progress="downloading asset versions")

    def get_asset_class_id(self, class_name):
        class_id = AssetClass.active_classes(store=self.store).get(class_name)
        if not class_id:
            self.user_log.info(f"asset-class: {class_name} not found locally, checking in remote")
            # fetch and check again
            self.download_class_list()
            class_id = AssetClass.get_id(store=self.store, name=class_name)
            if not class_id:
                raise exceptions.AssetClassNotFoundError(f"asset-class: {class_name} not found")
        return class_id

    def download_assets_for_class(self, class_id, show_progress=False, force=False):
        asset_class = AssetClass(id=class_id, store=self.store)
        self.download_asset_class(class_id=class_id)
        # we fetch only metadata here
        self.download_dir(
            dir_url=self.store.class_assets_url(class_id=class_id),
            dir_dst=asset_class.cache_dir,
            pattern=f"*{self.store.asset_file_name}",
            progress=f"downloading assets for class {class_id}:" if show_progress else None,
            force=force
        )
        self.create_asset_list_for_class(asset_class)

    def download_asset_classes(self, show_progress=False, force=False):
        self.download_dir(dir_url=self.store.asset_classes_url,
                          dir_dst=self.store.asset_classes_dir,
                          progress="downloading asset-class list" if show_progress else None,
                          force=force)
        return self.store.asset_classes_dir

    def download_class_list(self, force=False):
        """Downloads the class_list.yaml file of the project into the asset store"""
        self.download_file(file_url=self.store.class_list_url,
                           dst=self.store.class_list_file,
                           force=force)
        if not os.path.exists(self.store.class_list_file):
            raise exceptions.AssetException("failed to download the asset class-list")
        return self.store.class_list_file

    def download_asset_class(self, class_id, force=False):
        """Downloads the class-id.yaml file of the class_id into the asset store"""
        self.download_file(file_url=self.store.asset_class_url(class_id),
                           dst=self.store.asset_class_file(class_id),
                           force=force)
        if not os.path.exists(self.store.asset_class_file(class_id)):
            raise exceptions.AssetException(f"failed to download the asset-class file: {class_id}")
        return self.store.asset_class_file(class_id)

    def download_asset_file(self, class_id: str, seq_id: str, force=False):
        """Downloads the asset.yaml file into the asset store"""
        self.download_file(file_url=self.store.asset_file_url(class_id, seq_id),
                           dst=self.store.asset_file(class_id, seq_id),
                           force=force)
        if not os.path.exists(self.store.asset_file(class_id, seq_id)):
            raise exceptions.AssetException(f"failed to download the asset file: {class_id}/{seq_id}")
        return self.store.asset_file(class_id, seq_id)

    def fetch_asset_class(self, class_name=None, class_id=None):
        """downloads class-list along with class-data"""
        # try fetching from bucket
        # TODO: check if the class is in the deleted bucket directory, if yes raise AssetClassDeletedError
        self.download_class_list(force=True)
        class_id = class_id or AssetClass.get_id(store=self.store, name=class_name)
        if not class_id:
            raise exceptions.AssetClassNotFoundError(
                f"invalid class name or id, no asset-class found for {class_name or class_id}")
        # download asset class file if not present
        if not os.path.exists(self.store.asset_class_file(id=class_id)):
            self.download_asset_class(class_id=class_id, force=True)

    def create_asset_list_for_class(self, asset_class: AssetClass):
        """create assets_list.yaml file at the root of the class_dir
        we do this, so that everytime user calls assets list <class_name>
        we can just read from that file
        """
        class_dir = asset_class.cache_dir
        asset_files = list_files(root_dir=class_dir,
                                 pattern=f"*{self.store.asset_file_name}")
        all_assets = {}
        for asset_yaml in asset_files:
            data = FileUtils.read_yaml(asset_yaml)
            all_assets[data["seq_id"]] = data

        dst = os.path.join(class_dir, self.store.asset_list_file_name)
        FileUtils.write_yaml(abs_path=dst, data=all_assets)
        return dst

    def download_contents(self, contents: Iterable[Content], desc: str = None):
        # collect urls
        targets, proxy_targets = [], []
        for content in contents:
            if content.exists():
                continue
            if content.can_download:
                if content.is_proxy:
                    proxy_targets.append(content)
                else:
                    targets.append(content)
        if not targets and not proxy_targets:
            self.user_log.message("nothing to download")
            return False

        # group by storage
        groups = {}

        for content in targets:
            storage = StorageFactory.storage_for_url(src_url=content.remote_url)
            transporter = storage.get_transporter()
            saved = groups.get(storage.name, set())
            saved.add(transporter.get_download_resource(src=content.remote_url,
                                                        dst=content.cache_path,
                                                        src_hash=(content.hash_type, content.hash_value)))
            groups[storage.name] = saved

        # download storage by storage
        for storage_name, targets in groups.items():
            storage = StorageFactory.storage_with_name(name=storage_name)
            self.perform_download(targets=list(targets),
                                  storage=storage,
                                  progress=(desc or "downloading asset-contents"))

        # download proxy contents
        if not proxy_targets:
            return True
        # toggle to use content credentials
        # note: this one of the only two places we use content credentials
        # the other place is while creating proxy asset
        StorageCredentials.shared().use_content_credentials = True
        storage = StorageFactory.storage_for_url(src_url=proxy_targets[0].remote_url)
        transporter = storage.get_transporter()
        targets = [transporter.get_download_resource(src=content.remote_url,
                                                     dst=content.cache_path,
                                                     src_hash=(content.hash_type, content.hash_value)
                                                     ) for content in proxy_targets]
        self.perform_download(targets=targets,
                              storage=storage,
                              progress=desc or "downloading proxy-contents")
        # reset the flag
        StorageCredentials.shared().use_content_credentials = False
        return True

    def copy_objects(self, objects: List[AssetObject], dst_url: str, desc: str = None):
        # collect urls
        targets = [obj for obj in objects if obj.content.can_download]
        if not targets:
            self.user_log.message("nothing to copy")
            return False

        # group by storage
        groups = {}
        for obj in targets:
            storage = StorageFactory.storage_for_url(src_url=obj.content.remote_url)
            transporter = storage.get_transporter()
            saved = groups.get(storage.name, set())
            saved.add(transporter.get_copy_resource(src=obj.content.remote_url,
                                                    dst=os.path.join(dst_url, obj.path),
                                                    size=obj.content.size,
                                                    src_hash=(obj.content.hash_type, obj.content.hash_value)))
            groups[storage.name] = saved

        # copy storage by storage
        for storage_name, targets in groups.items():
            storage = StorageFactory.storage_with_name(name=storage_name)
            self.perform_copy(targets=list(targets),
                              storage=storage,
                              progress=(desc or "copying asset-contents"))

        return True

    def perform_copy(self, targets: [TransportResource], storage: AssetStorage, progress: str = None):
        pbar = Progress.progress_bar(total=len(targets), desc=progress) if progress else None
        transporter = storage.get_transporter()
        if pbar:
            for resource in targets:
                resource.callback = lambda x: pbar.update(1)
        try:
            transporter.copy(resources=targets)
            if pbar:
                pbar.close("done")
        except exceptions.AssetException as e:
            if pbar:
                pbar.close(self.user_log.colorize("failed", LogColors.ERROR))
            raise e
