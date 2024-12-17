import os
from time import time

from asset_contents import Content
from asset_core.store.asset_store import AssetStore
from asset_pluggy.storage.blob import StorageData
from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from asset_pluggy.storage.transporter import TransportResource
from asset_pluggy.storage.urls import StorageURL
from asset_utils.utils.log_utils import LoggingMixin, LogColors
from asset_utils.utils.progress import Progress


class Fetcher(LoggingMixin):
    store: AssetStore = None

    def __init__(self, store):
        self.store = store

    def download_dir(self, dir_url: str, dir_dst: str, pattern=None, progress: str = None, force=False):
        """downloads a directory from cloud bucket into target dir and maintains the
        relative paths of the directory contents
        """
        storage, targets = self.resources_in_dir(dir_url=dir_url,
                                                 dir_dst=dir_dst,
                                                 pattern=pattern,
                                                 force=force)
        if targets:
            self.perform_download(targets=targets, storage=storage, progress=progress)
        return targets

    def resources_in_dir(self, dir_url: str, dir_dst: str, pattern=None, force=False) -> tuple:
        if not dir_url.endswith("/"):
            dir_url += "/"
        if pattern:
            dir_url = os.path.join(dir_url, pattern)
        storage = StorageFactory.storage_for_url(src_url=dir_url)
        url = storage.get_storage_url(url_string=dir_url)
        blobs = storage.list_blobs(url=url)
        if not blobs:
            self.user_log.message(f"{dir_url} is empty, nothing to download")
            return storage, []
        targets = self.url_to_resource(storage=storage,
                                       src_url=url,
                                       blobs=blobs,
                                       dir_dst=dir_dst,
                                       force=force)
        if not targets:
            self.user_log.message("all files available, skipping download")
        return storage, targets

    def perform_download(self, targets: [TransportResource], storage: AssetStorage, progress: str = None):
        ts = time()
        pbar = Progress.progress_bar(total=len(targets), desc=progress) if progress else None
        transporter = storage.get_transporter()
        if pbar:
            for resource in targets:
                resource.callback = lambda x: pbar.update(1)
        try:
            transporter.download(resources=targets)
            if pbar:
                te = time()
                pbar.close(message=f"done - downloading {len(targets)} files took: {te - ts:.2f} sec")
        except Exception as e:
            if pbar:
                pbar.close(self.user_log.colorize("failed", LogColors.ERROR))
            raise e

        # verify checksum and update the hashlist file
        ts = time()
        pbar2 = Progress.progress_bar(desc="verifying checksum", total=len(targets)) if progress else None
        verified, unverified = [], []
        for resource in targets:
            if resource.verify_checksum():
                pbar2.update(1) if pbar2 else None
                verified.append(resource)
            else:
                unverified.append(resource)
        # update hashlist
        if verified:
            self.update_hashlist(verified)
        if progress:
            te = time()
            pbar2.close(f"done - verifying {len(verified)} files took: {te - ts:.2f} sec")
        if unverified:
            self.user_log.error(f"checksum validation failed for {len(unverified)} files")
            self.user_log.message("\n".join(map(lambda x: f"{x.dst}-{x.src_hash}", unverified)))

    def update_hashlist(self, resources: [TransportResource]):
        if not resources:
            return
        hashes = {self.hash_store_key(path=res.dst): Content.serialize_hash(*res.src_hash) for res in resources}
        self.store.hashlist_db.update(**hashes)

    def get_from_hash_list(self, path):
        return self.store.hashlist_db.file_hashes.get(self.hash_store_key(path=path))

    def url_to_resource(self, storage: AssetStorage,
                        src_url: StorageURL,
                        blobs: [StorageData],
                        dir_dst: str,
                        force=False) -> list:
        """Creates list of transport resources based on the source url and destination directory"""

        def dst_path(blob: StorageData, parent_url: StorageURL):
            return os.path.abspath(os.path.join(dir_dst, os.path.relpath(blob.name, parent_url.dir_name)))

        resources = []
        transporter = storage.get_transporter()
        for blob in blobs:
            resources.append(transporter.get_download_resource(src=blob.url,
                                                               dst=dst_path(blob, src_url),
                                                               src_hash=blob.get_hash()))
        if force:
            return resources
        targets = []
        for resource in resources:
            # download if not already exists
            if not os.path.exists(resource.dst):
                targets.append(resource)
            else:
                # file exists but hash doesn't exist
                # this could be a possible corruption, so we download afresh
                file_hash = self.store.hashlist_db.file_hashes.get(self.hash_store_key(path=resource.dst))
                if not file_hash:
                    targets.append(resource)
                else:
                    # file exists, hash exists but hashes don't match
                    ht, hv = Content.deserialize_hash(file_hash)
                    blob_ht, blob_hv = resource.src_hash
                    if not (ht == blob_ht and hv == blob_hv):
                        targets.append(resource)
        return targets

    def hash_store_key(self, path):
        """use the relative path as key because user can move the asset store location"""
        return os.path.relpath(path, self.store.project_dir)

    def download_file(self, file_url, dst, force=False):
        """Downloads a file from cloud bucket into target dir"""
        storage = StorageFactory.storage_for_url(src_url=file_url)
        blob = storage.get_blob(url_string=file_url)
        exists = False
        if os.path.exists(dst):
            file_hash = self.get_from_hash_list(path=dst)
            if file_hash:
                ht, hv = Content.deserialize_hash(file_hash)
                blob_ht, blob_hv = blob.get_hash()
                if ht == blob_ht and hv == blob_hv:
                    exists = True

        # if it exists, we don't need to re-download unless its forced
        if not force and exists:
            return

        transporter = storage.get_transporter()
        resource = transporter.get_download_resource(src=file_url, dst=dst, src_hash=blob.get_hash())
        self.perform_download(targets=[resource], storage=storage)
