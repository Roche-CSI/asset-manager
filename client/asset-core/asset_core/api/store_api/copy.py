import os

from asset_core.asset.asset_uploader import AssetUploader
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.asset.fetchers.fetcher import Fetcher
from asset_pluggy.storage.storage_factory import StorageFactory, AssetStorage
from .store import StoreAPI

PATH_SEPARATOR = "/"


class CopyAPI(StoreAPI):
    """
    A class used to copy objects from a source to a destination.
    """

    def __init__(self, store=None, repo=None):
        super().__init__(store, repo)
        self._src_storage = None
        self._dst_storage = None
        self._src_url = None
        self._dst_url = None
        self._recursive = None
        self._force = None
        self._skip_cmp = None

    def copy(self, src: str, dst: str, recursive: bool, force: bool, skip_cmp: bool):
        """Copies objects from a source to a destination.

        Parameters
        ----------
        src : str
            The source URL.
        dst : str
            The destination URL.
        recursive : bool
            If True, copies directories recursively.
        force : bool
            If True, overwrites existing files without asking.
        skip_cmp : bool
            If True, skips the comparison of source and destination objects.
        """
        self._src_storage = StorageFactory.storage_for_url(src_url=src)
        self._dst_storage = StorageFactory.storage_for_url(src_url=dst)
        self._src_url = self._src_storage.get_storage_url(url_string=src)
        self._dst_url = self._dst_storage.get_storage_url(url_string=dst)
        self._recursive = recursive
        self._force = force
        self._skip_cmp = skip_cmp

        if self._src_url.is_remote() and self._dst_url.is_remote():
            self.remote_copy_objects()
        elif self._src_url.is_remote() and not self._dst_url.is_remote():
            self.download_objects()
        elif not self._src_url.is_remote() and self._dst_url.is_remote():
            self.upload_objects()
        else:
            self.user_log.error("no url found, please check the src and dst urls")

    def sanitized_dir_urls(self) -> (str, str):
        """Sanitize the source and destination directory URLs based on the ending slash.

        Returns
        -------
        tuple
            A tuple containing the sanitized source and destination directory URLs.
        """
        dst_dir_url = self._dst_url.url
        # adjust the url based on ending slash
        if dst_dir_url.endswith(PATH_SEPARATOR):
            if self._src_url.url.endswith(PATH_SEPARATOR):
                src_dir_name = os.path.basename(self._src_url.dir_name)
            else:
                src_dir_name = os.path.basename(self._src_url.url)
            dst_dir_url = os.path.join(dst_dir_url, src_dir_name)
        # always add a trailing slash to directory for correct path_in_asset
        dst_dir_url += PATH_SEPARATOR
        src_dir_url = self._src_url.url if self._src_url.url.endswith(
            PATH_SEPARATOR) else self._src_url.url + PATH_SEPARATOR
        return src_dir_url, dst_dir_url

    def sanitized_dst_file_url(self) -> str:
        """Sanitize the destination file URL based on the existing file or directory.

        Returns
        -------
        str
            The sanitized destination file URL.
        """
        if self._dst_storage.url_is_file(self._dst_url):
            # dst_url is an existing file
            dst_file_url = self._dst_url.url
        elif self._dst_url.url.endswith(PATH_SEPARATOR) or self._dst_storage.list_blobs(url=self._dst_url):
            # dst_url is a directory
            dst_file_url = os.path.join(self._dst_url.url, os.path.basename(self._src_url.url))
        else:
            # dst_url is a new file
            dst_file_url = self._dst_url.url
        return dst_file_url

    def filtered_dir_blobs(self, src_blobs: list, dst_dir_url: str, storage: AssetStorage) -> list:
        """Filter the source blobs to determine which need to be copied.

        Filters the `src_blobs` to determine which blobs are duplicates, which are new and which need to be replaced.
        Log the number of new blobs, replace blobs, and skipped blobs.
        Ask the user for confirmation before replacing blobs based on the `force` attribute.

        Parameters
        ----------
        src_blobs : list
            A list of source blobs.
        dst_dir_url : str
            The destination directory URL.
        storage : AssetStorage
            The storage object to be used for filtering duplicate blobs.

        Returns
        -------
        list
            A final list of updated blobs that needs to be copied.
        """
        dst_blobs = self._dst_storage.list_blobs(url=dst_dir_url)
        # filter objects to be copied and objects to be replaced
        new_blobs, replace_blobs = storage.filter_duplicate_blobs(src_blobs, dst_blobs)
        if not new_blobs and not replace_blobs:
            self.user_log.message(f"All object(s) already exist at {dst_dir_url}")
            return None
        if new_blobs:
            self.user_log.info(f"\t- {len(new_blobs)} new object(s) will be copied")
        if replace_blobs:
            self.user_log.info(f"\t- {len(replace_blobs)} object(s) will be replaced")
        skipped = len(src_blobs) - len(new_blobs) - len(replace_blobs)
        if skipped:
            self.user_log.info(f"\t- {skipped} object(s) will be skipped")

        # confirm with user before replacing objects
        if not self._force and replace_blobs:
            user_input = self.user_log.ask_user(
                question=f"do you want to replace {len(replace_blobs)} object(s)?",
                options=["y", "n"],
                default="y"
            )
            if user_input != "y":
                self.user_log.alert(f"Skipped overwriting {len(replace_blobs)} object(s)")
                replace_blobs = []
        return new_blobs + replace_blobs

    def remote_copy_objects(self):
        """
        Copies a file or a directory from a remote source to a remote destination.
        """
        if not os.path.commonprefix([self._src_url.url, self._dst_url.url]):
            self.user_log.error("Trying to copy to a different storage platform, which is currently not supported")
            return

        if self._src_storage.url_is_file(self._src_url):
            # src_url is a file
            self.remote_copy_file()
        elif not self._recursive:
            self.user_log.alert(f"No file found at {self._src_url.url}")
            self.user_log.info("Are you trying to copy a directory? use --r option")
        else:
            # src_url is a directory
            self.remote_copy_dir()

    def remote_copy_dir(self):
        """
        Copies a directory from a remote source to a remote destination.
        """
        src_dir_url, dst_dir_url = self.sanitized_dir_urls()
        # get the list of objects to be copied
        src_blobs = self._src_storage.list_blobs(url=src_dir_url)
        self.user_log.info(f"Total {len(src_blobs)} object(s) found at {src_dir_url}")

        if not self._skip_cmp:
            # compare and update src_blobs with filtered objects
            src_blobs = self.filtered_dir_blobs(src_blobs, dst_dir_url, self._src_storage)

        if not src_blobs:
            self.user_log.message("Nothing to copy")
            return

        # create the transport resources to perform copy
        transporter = self._dst_storage.get_transporter()
        targets = []
        for blob in src_blobs:
            resource = transporter.get_copy_resource(src=blob.url,
                                                     dst=os.path.join(dst_dir_url, blob.path_in_asset),
                                                     src_hash=blob.get_hash(),
                                                     blob=blob)
            targets.append(resource)

        AssetFetcher(self.store).perform_copy(targets=targets,
                                              storage=self._dst_storage,
                                              progress="copying")
        self.user_log.success(f"Successfully copied {len(targets)} object(s) to {dst_dir_url}")

    def remote_copy_file(self):
        """
        Copies a file from a remote source to a remote destination.
        """
        dst_file_url = self.sanitized_dst_file_url()
        # get the blob object to be copied
        src_blob = self._src_storage.get_blob(url_string=self._src_url.url)
        # check if the dst_file_url already exists
        if not self._skip_cmp and self._dst_storage.blob_exists(url_string=dst_file_url):
            dst_blob = self._dst_storage.get_blob(url_string=dst_file_url)
            _, replace_blobs = self._src_storage.filter_duplicate_blobs([src_blob], [dst_blob])
            if not replace_blobs:
                self.user_log.message(f"Object already exist at {dst_file_url}, skipping copy")
                return
            # confirm with user before replacing objects
            if not self._force:
                user_input = self.user_log.ask_user(
                    question=f"a file already exists at: {dst_file_url}, do you want overwrite it?",
                    options=["y", "n"],
                    default="y"
                )
                if user_input != "y":
                    self.user_log.alert(f"Skipped overwriting {dst_file_url}")
                    return

        # create the transport resource to perform copy
        transporter = self._dst_storage.get_transporter()
        resource = transporter.get_copy_resource(src=src_blob.url,
                                                 dst=dst_file_url,
                                                 src_hash=src_blob.get_hash(),
                                                 blob=src_blob)
        AssetFetcher(self.store).perform_copy(targets=[resource],
                                              storage=self._dst_storage,
                                              progress="copying")
        self.user_log.success(f"Successfully copied object to {dst_file_url}")

    def download_objects(self):
        """
        Downloads a file or a directory from a remote source to a local destination.
        """
        if not self._skip_cmp and os.path.ismount(self._dst_url.url):
            # inform user
            user_input = self.user_log.ask_user(
                question=f"{self._dst_url.url} is a mounted drive, hash computation of files might take longer\n "
                         f"due to network latency, you can skip this by using the '--no_deduplicate' flag,\n"
                         f"do you want to proceed with '--no_deduplicate' flag",
                options=["y", "n"],
                default="y")
            self._skip_cmp = bool(user_input == "y")

        if self._src_storage.url_is_file(self._src_url):
            # src_url is a file
            self.download_file()
        elif not self._recursive:
            self.user_log.alert(f"No file found at {self._src_url.url}")
            self.user_log.info("Are you trying to copy a directory? use --r option")
        else:
            # src_url is a directory
            self.download_dir()

    def download_dir(self):
        """
        Downloads a directory from a remote source to a local destination.
        """
        src_dir_url, dst_dir_url = self.sanitized_dir_urls()
        # get the list of objects to be downloaded
        src_blobs = self._src_storage.list_blobs(url=src_dir_url)
        self.user_log.info(f"Total {len(src_blobs)} object(s) found at {src_dir_url}")

        if not self._skip_cmp:
            # compare and update src_blobs with filtered objects
            src_blobs = self.filtered_dir_blobs(src_blobs, dst_dir_url, self._src_storage)

        if not src_blobs:
            self.user_log.message("Nothing to copy")
            return

        # create the transport resources to perform download
        transporter = self._src_storage.get_transporter()
        targets = []
        for blob in src_blobs:
            resource = transporter.get_download_resource(src=blob.url,
                                                         dst=os.path.join(dst_dir_url, blob.path_in_asset),
                                                         src_hash=blob.get_hash())
            targets.append(resource)

        Fetcher(store=self.store).perform_download(targets=targets,
                                                   storage=self._src_storage,
                                                   progress="downloading")
        self.user_log.success(f"Successfully copied {len(targets)} objects to {dst_dir_url}")

    def download_file(self):
        """
        Downloads a file from a remote source to a local destination.
        """
        dst_file_url = self.sanitized_dst_file_url()
        # get the blob object to be uploaded
        src_blob = self._src_storage.get_blob(url_string=self._src_url.url)
        # check if the dst_file_url already exists
        if not self._skip_cmp and self._dst_storage.blob_exists(url_string=dst_file_url):
            dst_blob = self._dst_storage.get_blob(url_string=dst_file_url)
            _, replace_blobs = self._src_storage.filter_duplicate_blobs([src_blob], [dst_blob])
            if not replace_blobs:
                self.user_log.message(f"Object already exist at {dst_file_url}, skipping copy")
                return
            # confirm with user before replacing objects
            if not self._force:
                user_input = self.user_log.ask_user(
                    question=f"a file already exists at: {dst_file_url}, do you want overwrite it?",
                    options=["y", "n"],
                    default="y"
                )
                if user_input != "y":
                    self.user_log.alert(f"Skipped overwriting {dst_file_url}")
                    return

        # create the transport resource to perform download
        transporter = self._src_storage.get_transporter()
        resource = transporter.get_download_resource(src=src_blob.url,
                                                     dst=dst_file_url,
                                                     src_hash=src_blob.get_hash())
        Fetcher(store=self.store).perform_download(targets=[resource],
                                                   storage=self._src_storage,
                                                   progress="downloading")
        self.user_log.success(f"Successfully copied object to {dst_file_url}")

    def upload_objects(self):
        """
        Uploads a file or a directory from a local source to a remote destination.
        """
        if not self._skip_cmp and os.path.ismount(self._src_url.url):
            # inform user
            user_input = self.user_log.ask_user(
                question=f"{self._src_url.url} is a mounted drive, hash computation of files might take longer\n "
                         f"due to network latency, you can skip this by using the '--no_deduplicate' flag,\n"
                         f"do you want to proceed with '--no_deduplicate' flag",
                options=["y", "n"],
                default="y")
            self._skip_cmp = bool(user_input == "y")

        if not self._src_storage.blob_exists(url_string=self._src_url.url):
            self.user_log.alert(f"No such file or directory: {self._src_url.url}")
            return
        elif self._src_storage.url_is_file(self._src_url):
            # src_url is a file
            self.upload_file()
        elif not self._recursive:
            self.user_log.alert(f"{self._src_url.url} is not a file")
            self.user_log.info("Are you trying to copy a directory? use --r option")
        else:
            # src_url is a directory
            self.upload_dir()

    def upload_dir(self):
        """
        Uploads a directory from a local source to a remote destination.
        """
        src_dir_url, dst_dir_url = self.sanitized_dir_urls()
        # get the list of objects to be uploaded
        src_blobs = self._src_storage.list_blobs(url=src_dir_url)
        self.user_log.info(f"Total {len(src_blobs)} object(s) found at {src_dir_url}")

        if not self._skip_cmp:
            # compare and update src_blobs with filtered objects
            src_blobs = self.filtered_dir_blobs(src_blobs, dst_dir_url, self._dst_storage)

        if not src_blobs:
            self.user_log.message("Nothing to copy")
            return

        # create the transport resources to perform upload
        transporter = self._dst_storage.get_transporter()
        targets = []
        for blob in src_blobs:
            resource = transporter.get_upload_resource(src=blob.name,
                                                       dst=os.path.join(dst_dir_url, blob.path_in_asset),
                                                       src_hash=None)
            targets.append(resource)

        AssetUploader(asset=None).perform_upload(targets=targets,
                                                 storage=self._dst_storage,
                                                 progress="uploading")
        self.user_log.success(f"Successfully copied {len(targets)} objects to {dst_dir_url}")

    def upload_file(self):
        """
        Uploads a file from a local source to a remote destination.
        """
        dst_file_url = self.sanitized_dst_file_url()
        # get the blob object to be uploaded
        src_blob = self._src_storage.get_blob(url_string=self._src_url.url)
        # check if the dst_file_url already exists
        if not self._skip_cmp and self._dst_storage.blob_exists(url_string=dst_file_url):
            dst_blob = self._dst_storage.get_blob(url_string=dst_file_url)
            _, replace_blobs = self._dst_storage.filter_duplicate_blobs([src_blob], [dst_blob])
            if not replace_blobs:
                self.user_log.message(f"Object already exist at {dst_file_url}, skipping copy")
                return
            # confirm with user before replacing objects
            if not self._force:
                user_input = self.user_log.ask_user(
                    question=f"a file already exists at: {dst_file_url}, do you want overwrite it?",
                    options=["y", "n"],
                    default="y"
                )
                if user_input != "y":
                    self.user_log.alert(f"Skipped overwriting {dst_file_url}")
                    return

        # create the transport resource to perform upload
        transporter = self._dst_storage.get_transporter()
        resource = transporter.get_upload_resource(src=src_blob.name,
                                                   dst=dst_file_url,
                                                   src_hash=None)
        AssetUploader(asset=None).perform_upload(targets=[resource],
                                                 storage=self._dst_storage,
                                                 progress="uploading")
        self.user_log.success(f"Successfully copied object to {dst_file_url}")
