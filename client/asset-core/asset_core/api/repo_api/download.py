import fnmatch
import os
from time import time

from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_utils.common.exceptions import AssetException
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.progress import Progress
from .repo import RepoAPI


class DownloadAPI(RepoAPI):

    def download_asset(self, files: list = None):
        if len(self.asset.contents) == 0:
            self.user_log.message("asset is empty, nothing to download")
            return

        missing_objects = self._find_missing_objects(files=files)
        if not missing_objects:
            self.user_log.info("all files available - you are all set")
            return

        self.user_log.message(f"downloading {len(missing_objects)} files")

        # download contents
        try:
            fetcher = AssetFetcher(store=self.asset.repo.store)
            fetcher.download_contents(contents=[obj.content for obj in missing_objects])
        except AssetException as e:
            e.logs.add(e.msg)
            e.logs.add(UserCommands().download_asset(with_credential=True))
            e.msg = f"failed to download files for asset-{self.asset.name}"
            raise

        # link files
        ts = time()
        pbar = Progress.progress_bar(desc=f"linking files for asset-{self.asset.name}",
                                     total=len(missing_objects))
        status = self.asset.objects.link(callback=lambda x: pbar.update(1),
                                         selected=missing_objects)
        te = time()
        pbar.close(message=f"done - linking {len(missing_objects)} files took: {te - ts:.2f} sec "
                           f"using linking type: {os.getenv('ASSET_OBJECT_LINKING') or 'copy'}")

        message = ""
        for obj in status:
            if not status[obj]:
                message += f" - {obj.path}\n"
        if message:
            e = AssetException("failed to link, files not available locally")
            e.logs.add(message)
            raise e
        else:
            self.user_log.success("success: completed - you are all set")

        self.user_log.message(UserCommands().asset_info())

    def _find_missing_objects(self, files: list = None):
        # check for missing objects
        missing_objects = self.asset.objects.unlinked() or []
        if not files or not missing_objects:
            return missing_objects

        # normalize path
        paths = set([self.asset.repo.normalize_filepath(path) for path in files])
        globs, non_globs = set(), set()
        for path in paths:
            if "*" or "?" in path:
                globs.add(path)
            else:
                non_globs.add(path)

        matched = []
        for obj in missing_objects:
            if obj.path in non_globs:
                matched.append(obj)
            else:
                # check if user passed any glob string
                for glob in globs:
                    if fnmatch.fnmatch(obj.path, glob):
                        matched.append(obj)

        return matched
