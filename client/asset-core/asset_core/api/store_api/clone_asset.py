import fnmatch
import os
import shutil
import tempfile
from time import time
from typing import List

from asset_core.api.repo_api.info import InfoAPI
from asset_core.asset.asset import Asset
from asset_core.asset.asset_class import AssetClass
from asset_core.asset.asset_diff import AssetDiff
from asset_core.asset.asset_handle import AssetHandle
from asset_core.asset.asset_snapshot import AssetSnapshot
from asset_core.asset.asset_uploader import AssetUploader
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.objects.asset_object import AssetObject, ObjectViews
from asset_core.store.repo import Repo
from asset_pluggy.storage.storage_factory import StorageFactory
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands, ASSET_INFO
from asset_utils.utils import ch_dir
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import colored_string, LogColors
from asset_utils.utils.progress import Progress
from .find import FindAPI
from .store import StoreAPI


class CloneAssetAPI(StoreAPI):
    """API for cloning assets from remote to local or remote to remote."""

    def run(self, args):
        pass

    def remote_clone(self, asset_name: str, remote_url: str):
        """Clones the asset from remote to another remote location."""
        fetcher = AssetFetcher(store=self.store)
        try:
            # check validity and access control
            handle = self._is_valid_remote_asset(fetcher=fetcher, asset_name=asset_name)
            handle.check_access_control(fetcher=fetcher)
            self.user_log.info(f"asset can be cloned: {asset_name}")
        except exceptions.AssetException as e:
            e.logs.add(f"unable to clone asset: {asset_name}", color=LogColors.INFO)
            raise

        # url where the asset will be cloned
        remote_url = os.path.join(remote_url, handle.class_name, handle.seq_id)

        # download asset meta data at asset-store
        self._download_asset_metadata(fetcher=fetcher, handle=handle)

        with tempfile.TemporaryDirectory() as temp_dir:
            # create .asset inside the directory
            self.repo = Repo.create_repo(root_dir=temp_dir, force=True)
            # download raw asset
            raw_asset = self._load_from_repo(repo=self.repo, handle=handle, view=Asset.views.RAW)
            raw_objects = raw_asset.objects.filter(predicate=lambda x: x.has_raw_mode)
            self._download_objects(asset=raw_asset,
                                   fetcher=fetcher,
                                   objects=raw_objects,
                                   desc="downloading asset-raw")
            raw_asset.set_as_current(repo=self.repo)
            # check if a snapshot needs to be created
            self._upload_snapshot(asset=raw_asset)
            # load asset objects to be cloned
            data_asset = self._load_from_repo(repo=self.repo, handle=handle, view=Asset.views.DATA)
            data_objects = data_asset.objects.filter(predicate=lambda x: not x.has_raw_mode)
            if handle.extras:
                data_objects = [obj for obj in data_objects if fnmatch.fnmatch(obj.path, handle.extras)]
            if not data_objects:
                self.user_log.info(f"{asset_name} is empty - nothing to clone")
                self.store.remove_repo(repo_id=self.repo.id)
                return

            # check if the objects already exist in the remote url
            new_objects, replace_objects = self.filter_remote_objects(objects=data_objects, url=remote_url)
            if not new_objects and not replace_objects:
                self.user_log.info(f"asset already exists at {remote_url}, skip cloning")
                self.store.remove_repo(repo_id=self.repo.id)
                return

            try:
                # replace existing objects
                self._copy_objects(fetcher=fetcher,
                                   objects=replace_objects,
                                   remote_url=remote_url,
                                   desc="replacing existing objects")
                # copy new objects
                self._copy_objects(fetcher=fetcher,
                                   objects=new_objects,
                                   remote_url=remote_url,
                                   desc="copying new objects")

                # create an asset info file and upload it to the same remote url
                asset_info = os.path.join(self.repo.fs_path, "asset_info.txt")
                self._create_asset_info(asset=data_asset, file=asset_info)
                uploader = AssetUploader(asset=data_asset)
                uploader.upload_object(file=asset_info, dst_url=remote_url)
            except exceptions.AssetException as e:
                e.logs.add("asset cloning was unsuccessful, please try again", color=LogColors.INFO)
                raise
            finally:
                # remove the asset from store
                self.store.remove_repo(repo_id=self.repo.id)

        self.user_log.success(f"Successfully cloned {asset_name}")
        self.user_log.info(f"asset cloned at {remote_url}")

    def filter_remote_objects(self, objects: List[AssetObject],
                              url: str) -> (List[AssetObject], List[AssetObject]):
        # TODO: aws blobs don't have md5 hash, need to find a way to compare
        remote_url = url + "/" if not url.endswith("/") else url  # make sure url ends with '/' for path comparison
        storage = StorageFactory.storage_for_url(src_url=remote_url)
        remote_blobs = storage.list_blobs(url=remote_url)
        blob_hashes = {blob.path_in_asset: blob.hashes.get('md5') for blob in remote_blobs}
        new_objects, replace_objects = [], []
        for obj in objects:
            if obj.path not in blob_hashes:
                new_objects.append(obj)
            elif obj.content.hash_value != blob_hashes[obj.path]:
                replace_objects.append(obj)
        return new_objects, replace_objects

    def _create_asset_info(self, asset: Asset, file: str):
        with open(file, "w") as f:
            f.writelines([f"Asset Name:\t {asset.name}\n",
                          f"Asset Class:\t {asset.asset_class.name}\n",
                          f"Asset Seq ID:\t {asset.seq_id}\n",
                          f"Asset Version:\t {asset.version.number}\n",
                          f"Asset ID:\t {asset.id}\n",
                          f"Created By:\t {asset.created_by}\n",
                          f"Created At:\t {asset.created_at}\n",
                          f"Remote URL:\t {asset.remote_url}\n"])

    def clone_asset(self, asset_name,
                    target_dir=None,
                    force=False,
                    recursive=False,
                    soft=False,
                    version=None):
        """Clones the asset from remote to local."""
        asset_linking_type = os.getenv("ASSET_OBJECT_LINKING") or "copy"
        # check linking type and ask for user confirmation to proceed
        if asset_linking_type != "copy":
            user_choice = self.user_log.ask_user(
                question=f"asset linking type is '{asset_linking_type}', change tracking and updates will be disabled."
                         f" do you wish to continue?",
                options=["y", "n"], default="y"
            )
            if user_choice.lower() == "n":
                self.user_log.info("cloning aborted. update 'linking_type' using asset config.")
                self.user_log.message(UserCommands().set_user_configs())
                return

        if recursive:
            # clone the asset and all the refs it depends on
            return self.perform_recursive_cloning(name=asset_name,
                                                  target_dir=target_dir,
                                                  force=force,
                                                  soft=soft,
                                                  version=version)
        else:
            return self.perform_cloning(name=asset_name,
                                        target_dir=target_dir,
                                        force=force,
                                        soft=soft,
                                        version=version)

    def perform_recursive_cloning(self, name, target_dir, force, soft, version):
        """Clone the asset and all the inputs it depends on."""
        refs, sanitized_name = InfoAPI.list_remote_refs(asset_name=name,
                                                        project_id=self.store.project_id)
        if refs and refs.get("depends_on"):
            items = [ref.src_version.get("name") for ref in refs.get("depends_on")]
            items.insert(0, sanitized_name)
            self.user_log.info("The following assets will be downloaded:")
            self.user_log.message(items, bulleted=True)
            user_input = self.user_log.ask_user(question="do you wish to continue?",
                                                options=["y", "n"], default="y")
            if user_input.lower() == "y":
                cloned = {}
                for asset in items:
                    asset_info = self.perform_cloning(name=str(asset),
                                                      target_dir=target_dir,
                                                      force=force,
                                                      soft=soft,
                                                      version=version)
                    cloned = {**cloned, **asset_info}
                return cloned

    def perform_cloning(self, name, target_dir, force, soft, version):
        return self.__clone_individual_asset(name=name,
                                             target_dir=target_dir,
                                             force=force,
                                             soft=soft,
                                             version=version)

    def __clone_individual_asset(self, name,
                                 target_dir=None,
                                 force=False,
                                 soft=False,
                                 version=None) -> dict:
        """Clones the asset from remote to local
        - check if asset is cloneable i.e. it's a valid name
        - create asset repo dir at the target dir
        - create .asset inside the directory
        - fetch asset yamls
        - construct the manifest file
        - make copy on write of files from asset_store
        - download the missing files from cloud

        Returns
        -------
        dict
            The cloned asset name and the target directory.
        """
        fetcher = AssetFetcher(store=self.store)
        try:
            # check validity and access control
            handle = self._is_valid_remote_asset(fetcher=fetcher, asset_name=name, version=version)
            handle.check_access_control(fetcher=fetcher)
        except exceptions.AssetException as e:
            e.logs.add(f"unable to clone asset: {name}", color=LogColors.INFO)
            raise

        # create the asset repo at the target dir
        asset_dst = self._get_asset_dst(handle=handle, target_dir=target_dir, force=force)
        # download asset metadata at asset-store
        self._download_asset_metadata(fetcher=fetcher, handle=handle)
        # update the asset_list.yaml for the asset class
        self._update_asset_list(fetcher=fetcher, handle=handle)

        # download asset contents
        with ch_dir(asset_dst):
            # create repo, i.e .asset inside the directory
            self.repo = Repo.create_repo(force=force)
            # store the linking type in the repo (repo.json)
            self.repo.linking_type = os.getenv("ASSET_OBJECT_LINKING") or "copy"
            # download raw asset first
            raw_asset = self._load_from_repo(repo=self.repo, handle=handle, view=Asset.views.RAW)
            raw_objects = raw_asset.objects.filter(predicate=lambda x: x.has_raw_mode)
            self._download_objects(asset=raw_asset,
                                   fetcher=fetcher,
                                   objects=raw_objects,
                                   desc="downloading asset-raw")
            raw_asset.set_as_current(repo=self.repo)
            # check if a snapshot needs to be uploaded
            self._upload_snapshot(asset=raw_asset)
            if soft:
                self._print_user_message(asset_name=handle.asset_name, asset_dst=asset_dst, soft=soft)
                return {raw_asset.version.name: asset_dst}

            # download data asset
            data_asset = self._load_from_repo(repo=self.repo, handle=handle, view=Asset.views.DATA)
            data_objects = data_asset.objects.filter(predicate=lambda x: not x.has_raw_mode)
            # download both raw and data contents
            if handle.extras:
                data_objects = [obj for obj in data_objects if fnmatch.fnmatch(obj.path, handle.extras)]
                if not data_objects:
                    # clean up if nothing to download
                    self.store.remove_repo(repo_id=self.repo.id)
                    shutil.rmtree(asset_dst)
                    # raise exception
                    e = exceptions.AssetException(f"no matching files found for pattern: {handle.extras}")
                    e.logs.add("please check the pattern: {handle.extras} and try again", LogColors.INFO)
                    raise e

            self._download_objects(asset=data_asset,
                                   fetcher=fetcher,
                                   objects=data_objects,
                                   desc="downloading asset-data")

        self._print_user_message(asset_name=handle.asset_name, asset_dst=asset_dst, soft=soft)
        return {data_asset.version.name: asset_dst}

    def _upload_snapshot(self, asset: Asset):
        """Create and upload the snapshot file for the asset if necessary."""
        if AssetSnapshot.is_snapshot_version(asset.version.number) and not os.path.exists(asset.snapshot_file):
            asset_snapshot = AssetSnapshot(store=self.store)
            asset_snapshot.create_from_manifest(manifest_file=asset.cached_manifest_file)
            asset_snapshot.upload(class_id=asset.asset_class.id,
                                  seq_id=str(asset.seq_id),
                                  version=asset.version.number)

    def _download_asset_metadata(self, fetcher: AssetFetcher, handle: AssetHandle):
        """Download the necessary asset metadata into the asset store.

        Necessary metadata includes:
        - asset.yaml (already downloaded by AssetHandle)
        - an object snapshot file (depending on the version)
        - some version_*.yaml files (depending on the snapshot and version)
        - objects_v2/ directory
        """
        asset_snapshot = AssetSnapshot(store=self.store)
        latest_snapshot = asset_snapshot.latest_remote_snapshot(class_id=handle.class_id,
                                                                seq_id=handle.seq_id,
                                                                version=handle.version)
        # download the latest snapshot file if it exists
        if latest_snapshot:
            asset_snapshot.download(class_id=handle.class_id,
                                    seq_id=handle.seq_id,
                                    version=latest_snapshot)

        # download the necessary version yaml files
        fetcher.download_snapshot_versions(class_id=handle.class_id,
                                           seq_id=handle.seq_id,
                                           snapshot_version=latest_snapshot,
                                           target_version=handle.version)

        # download the objects_v2 directory
        fetcher.download_asset_objects(class_id=handle.class_id,
                                       seq_id=handle.seq_id,
                                       show_progress=True)

    def _load_from_repo(self, repo, handle: AssetHandle, view: ObjectViews):
        """downloads the asset in raw mode"""
        asset_name = Asset.asset_name(class_name=handle.class_name, seq_id=handle.seq_id)
        # the status of asset or class might have changed, so we need to create a new manifest
        manifest_file = AssetDiff().create_asset_manifest(repo=repo,
                                                          asset_name=asset_name,
                                                          ver_number=handle.version,
                                                          force=True)

        asset = Asset(repo=self.repo, load=False, view=view)
        asset.de_serialize(data=FileUtils.read_json(manifest_file))
        return asset

    def _download_objects(self, asset, fetcher, objects: List[AssetObject], desc: str) -> None:
        if not len(objects):
            return
        fetcher.download_contents(contents=[obj.content for obj in objects], desc=desc)

        # link the objects to the asset
        start_time = time()
        pbar = Progress.progress_bar(desc="linking objects", total=len(objects))
        asset.objects.link(selected=objects,
                           linking_type=self.repo.linking_type,
                           callback=lambda x: pbar.update(1))
        pbar.close(message=f"done - linking {len(objects)} files took: {time() - start_time:.2f} sec "
                           f"using linking type: {self.repo.linking_type}")

    def _copy_objects(self, fetcher, objects: List[AssetObject], remote_url: str, desc: str) -> None:
        if not len(objects):
            return
        fetcher.copy_objects(objects=objects, dst_url=remote_url, desc=desc)

    def _print_user_message(self, asset_name, asset_dst, soft=False):
        asset_dir_relpath = os.path.relpath(asset_dst, os.getcwd())
        if asset_dir_relpath == ".":
            # already inside the asset dir
            cmd = UserCommands().asset_info()
        else:
            cmd = colored_string(f"(cd {asset_dir_relpath} && {ASSET_INFO.get('cmd')})", LogColors.COMMAND)
            cmd = f"use: {cmd} --> {ASSET_INFO.get('desc')}"
        msg = colored_string("Success", LogColors.SUCCESS)
        msg += f"\nasset: {asset_name} is {'soft' if soft else ''} cloned {'' if soft else 'and ready to use'}"
        msg += f"\n{cmd}"
        self.user_log.message(msg)

    def _is_valid_remote_asset(self, fetcher: AssetFetcher,
                               asset_name: str,
                               version=None) -> AssetHandle:
        """Verify the asset name and check if the version exists in remote.

        - check if the asset is temp/local
        - fetch and update the class_id
        - fetch and update the seq_id if alias is provided
        - check if the asset version exists in remote

        Returns
        -------
        AssetHandle
            The asset handle object with all the necessary fields.
        """
        handle = AssetHandle.from_name(asset_name=asset_name, version=version)
        # if temp asset, can't be downloaded
        if handle.is_temp():
            raise exceptions.AssetException(
                f"unable to clone asset, {asset_name} is a local asset has not been uploaded yet")

        # check asset validity and access control
        find_api = FindAPI(store=self.store)
        if not handle.is_valid(fetcher=fetcher, find_api=find_api):
            raise exceptions.InvalidAssetNameError(f"invalid asset name: {asset_name}")

        # check if the asset exists in remote
        if not self._asset_exists(fetcher=fetcher, handle=handle):
            raise exceptions.InvalidAssetNameError(f"invalid asset name: {asset_name} or version: {handle.version}")

        return handle

    def _asset_exists(self, fetcher: AssetFetcher, handle: AssetHandle) -> bool:
        """Checks if the asset exists in remote

        Parameters
        ----------
        fetcher: AssetFetcher
            The asset fetcher object.
        handle: AssetHandle
            The asset handle object.

        Returns
        -------
        bool
            True if the asset exists in remote, False otherwise.
        """
        pbar = Progress.status_bar(desc=f"checking if asset exists ({handle.asset_name})")
        exists = fetcher.verify_asset_exists(class_id=handle.class_id, seq_id=handle.seq_id, version=handle.version)
        if exists:
            pbar.close(message="done: found asset")
            return True

        pbar.close(message="error: asset not found")
        self.user_log.error(f"asset: {handle.asset_name} not found in remote - invalid asset")
        self.user_log.message(UserCommands().list_assets())
        return False

    def _get_asset_dst(self, handle: AssetHandle,
                       target_dir: str = None,
                       force: bool = False) -> str:
        """Returns the target directory where the asset can be cloned

        We need to do 3 checks to ensure that the target dir is not violating the nested asset rule
        1. the target directory is inside an asset repo. violates nested asset rule.
        2. the target directory contains an asset as a child. violates nested asset rule.
        3. the target directory itself is an asset repo (contains .asset). check for force flag.

        Parameters
        ----------
        handle: AssetHandle
            The asset handle object.
        target_dir: str
            The target directory where the asset will be cloned.
        force: bool
            The force flag to override the existing asset.

        Returns
        -------
        str
            The target directory where the asset can be cloned.
        """
        # if user didn't pass target_dir then we create one with asset_name
        # prefer alias to seq_id for local directory naming
        dst = target_dir or os.path.join(os.getcwd(), handle.class_name, handle.alias or handle.seq_id)

        try:
            existing_repo = Repo(root=dst)
        except exceptions.NotAssetRepoError:
            # no existing repo found, can clone at dst directory
            # create the target directory if it doesn't exist
            if not os.path.exists(dst):
                os.makedirs(dst, exist_ok=True)
            return dst
        except exceptions.NestedRepoError as e:
            # Case 1 or 2: violation of nested asset rule, cannot clone
            e.msg = f"Unable to clone, {e.msg}"
            e.logs.add(colored_string(f"{e.data.get('repo')}", LogColors.INFO))
            e.logs.add(f"cannot clone at: {dst}")
            e.logs.add("Please select a different location")
            raise

        # Case 3: we have an existing asset repo at dst directory
        # check force flag to decide if we can override
        if existing_repo:
            if not force:
                e = exceptions.RepoOverwriteError(f"an asset already exists at: {dst}")
                e.logs.add("use '--force' to overwrite the existing asset", color=LogColors.INFO)
                raise e
            else:
                self.user_log.info(f"reusing existing asset repo: {dst}")

        return dst

    def _update_asset_list(self, fetcher: AssetFetcher, handle: AssetHandle):
        """Updates the asset_list.yaml for the asset class."""
        pbar = Progress.status_bar(desc=f"constructing asset list for class: {handle.class_name}")
        fetcher.create_asset_list_for_class(AssetClass(id=handle.class_id, store=self.store))
        pbar.close("done")
