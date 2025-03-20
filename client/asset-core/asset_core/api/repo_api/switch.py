import os.path

from asset_core.asset.asset import Asset
from asset_core.asset.asset_diff import AssetDiff
from asset_core.asset.asset_snapshot import AssetSnapshot
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import colored_string, LogColors
from asset_utils.utils.progress import Progress
from .repo import RepoAPI

VERSION_YAML_FILE_NAME_FORMAT = "version_{ver_number}.yaml"


class SwitchAssetAPI(RepoAPI):

    def run(self, args):
        pass

    def switch_to_latest(self, force=False) -> bool:
        """Switches the current asset to the latest version.

        Download the latest version files if they are not available locally.

        Parameters
        ----------
        force : bool, optional
            Whether to force the switch without asking the user for confirmation, by default False.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        fetcher = AssetFetcher(store=self.store)
        latest_version = fetcher.get_version_from_bucket(class_id=self.asset.asset_class.id,
                                                         seq_id=str(self.asset.seq_id))
        if not latest_version:
            raise exceptions.AssetNotFoundError(f"can not find version data for asset: {self.asset.name}")

        latest_version_num = latest_version.get('number')
        self.user_log.info(f"latest version of asset: {self.asset.name} is: {latest_version_num}")
        if self.asset.version.number == latest_version_num:
            self.user_log.info("latest version is already active, nothing to pull")
            return True

        # check if the latest version is available locally
        version_file = os.path.join(self.asset.cache_dir,
                                    VERSION_YAML_FILE_NAME_FORMAT.format(ver_number=latest_version_num))
        if not os.path.exists(version_file):
            # fetch the necessary snapshot and version files
            asset_snapshot = AssetSnapshot(store=self.store)
            latest_snapshot = asset_snapshot.latest_remote_snapshot(class_id=self.asset.asset_class.id,
                                                                    seq_id=str(self.asset.seq_id),
                                                                    version=latest_version_num)
            # download the latest snapshot file if it exists
            if latest_snapshot:
                asset_snapshot.download(class_id=self.asset.asset_class.id,
                                        seq_id=str(self.asset.seq_id),
                                        version=latest_snapshot)

            # download the necessary version yaml files
            fetcher.download_snapshot_versions(class_id=self.asset.asset_class.id,
                                               seq_id=str(self.asset.seq_id),
                                               snapshot_version=latest_snapshot,
                                               target_version=latest_version_num)

            # update the objects_v2 directory
            fetcher.download_asset_objects(class_id=self.asset.asset_class.id,
                                           seq_id=str(self.asset.seq_id),
                                           show_progress=True)

        return self.switch_to_version(ver_number=latest_version_num, ask_confirmation=not force)

    def switch_to_version(self, ver_number: str, ask_confirmation=True) -> bool:
        """Switches the current asset to a specified version.

        Do not download the version files. Let the user know that they are not available locally.

        Parameters
        ----------
        ver_number : str
            The version number to switch to.
        ask_confirmation : bool, optional
            Whether to ask the user for confirmation before switching, by default True.

        Returns
        -------
        bool
            True if the switch was successful, False otherwise.
        """
        prev_asset = self.asset
        if prev_asset.version.number == ver_number:
            self.user_log.info(f"asset: {prev_asset.name}, version: {prev_asset.version.number} is already active")
            return True

        # check if the version number is valid and version file is available
        self.validate_version(version_number=ver_number)

        # check staged and unstaged changes
        if not self.can_switch_version(asset=prev_asset, ask_confirmation=ask_confirmation):
            return False

        # create the version manifest file
        pbar = Progress.status_bar(desc=f"creating meta information for version: {ver_number}")
        manifest_file = AssetDiff().create_asset_manifest(repo=self.asset.repo,
                                                          asset_name=self.asset.name,
                                                          ver_number=ver_number)
        asset = Asset(repo=self.asset.repo, id=self.asset.id, load=False)
        asset.de_serialize(data=FileUtils.read_json(manifest_file))
        asset.set_as_current()
        pbar.close(message="done")

        # update the asset objects
        self.update_asset_objects(cur_asset=asset, prev_asset=prev_asset)

        self.user_log.success("Success")
        self.user_log.info(f"asset: {asset.name}, version: {asset.version.number} is now active")
        return True

    def update_asset_objects(self, cur_asset: Asset, prev_asset: Asset):
        """Unlink and link the asset objects."""
        # download the asset contents
        fetcher = AssetFetcher(store=cur_asset.repo.store)
        fetcher.download_contents(contents=cur_asset.contents)

        # unlink the existing asset files
        pbar = Progress.progress_bar(total=len(prev_asset.objects),
                                     desc=f"unlinking files for previous version: {prev_asset.version.number}")
        prev_asset.objects.unlink(callback=lambda x: pbar.update(1))
        pbar.close("done")

        # link the new asset files
        pbar = Progress.progress_bar(total=len(cur_asset.objects),
                                     desc=f"linking files for version: {cur_asset.version.number}")
        cur_asset.objects.link(callback=lambda x: pbar.update(1))
        pbar.close("done")

    def validate_version(self, version_number: str):
        """Checks if the version number is valid for the asset."""
        version_file = os.path.join(self.asset.cache_dir,
                                    VERSION_YAML_FILE_NAME_FORMAT.format(ver_number=version_number))
        # first, check if the version file exists locally
        if os.path.exists(version_file):
            return

        # then, check if the version exists remotely
        fetcher = AssetFetcher(store=self.store)
        if not fetcher.verify_asset_exists(class_id=self.asset.asset_class.id,
                                           seq_id=str(self.asset.seq_id),
                                           version=version_number):
            raise exceptions.InvalidVersionError(f"invalid asset version: {version_number}")

        # exists remotely, but not available locally
        self.user_log.info(f"version: {version_number} not available locally. fetch it first.")
        self.user_log.info(UserCommands().fetch_asset())

    def can_switch_version(self, asset: Asset, ask_confirmation=True) -> bool:
        """Checks if it's possible to switch to a different version of the asset.

        Check if there are staged and unstaged changes to the current version.
        if there are unstaged changes, we must ask the user to stage or lose before proceeding.

        Parameters
        ----------
        asset : Asset
            The asset to check for the possibility of switching versions.
        ask_confirmation : bool, optional
            Whether to ask the user for confirmation if unstaged changes are found, by default True.

        Returns
        -------
        bool
            True if it's safe to switch versions, False otherwise.
        """
        # TODO : should we have merge of different versions, how does the user migrate the staged changes
        #     to a new version. For example,
        #     A is making some changes to genetics/1/version0.0.0, in the meantime
        #     B made some changes to genetics/1/version0.0.0 and uploaded i.e. version0.0.1
        #     A did a asset fetch, which shows a new version of the asset
        #     But if A switches to the new version A will lose all the changes
        #     This feature will require merge conflict feature also, for example
        #     If we automatically apply the changes to the newer version, and this scenario happens
        #     - version0.0.1 has a file that has been removed or modified
        #     - the unstaged changes of version0.0.0 has the same file modified or removed
        #     there is a conflict here (possibly many more such scenarios)
        unstaged_changes = AssetDiff().unstaged_changes(asset=asset)
        if unstaged_changes:
            self._print_unstaged_changes(changes=unstaged_changes)
            return self._confirm_version_switch(ask_confirmation=ask_confirmation)

        return True

    def _confirm_version_switch(self, ask_confirmation=True) -> bool:
        """Asks the user if they want to proceed with switching versions, considering unstaged changes.

        Parameters
        ----------
        ask_confirmation : bool, optional
            Whether to actually prompt the user, by default True.

        Returns
        -------
        bool
            True if the user decides to proceed, False otherwise.
        """
        msg = "please choose: \n"
        msg += "1 continue (I am fine with losing the changes)\n"
        msg += "2 abort \n"
        user_input = self.user_log.ask_user(question=msg, options=['1', '2'], default='1',
                                            ask_confirmation=ask_confirmation)
        if not user_input or user_input not in ['1', '2']:
            self.user_log.error('invalid option')
            return False
        if user_input == '2':
            self.user_log.info('aborted')
            return False

        return True

    def _print_unstaged_changes(self, changes: dict) -> None:
        """Prints the unstaged changes from the asset."""
        self.user_log.info(
            "you have unstaged changes to the current version, if you switch, you will lose these changes")

        columns = {
            "section": "",
            "details": "",
        }

        data = []
        if changes.get("deleted"):
            data += [{"section": colored_string("deleted: ", LogColors.ALERT),
                      "details": colored_string(obj.path, LogColors.ALERT)}
                     for obj in changes.get("deleted")]

        if changes.get("modified"):
            data += [{"section": colored_string("modified: ", LogColors.ALERT),
                      "details": colored_string(obj.path, LogColors.ALERT)}
                     for obj in changes.get("modified")]

        self.user_log.table(columns=columns, rows=data, table_fmt="plain")
