from asset_core.asset.asset import Asset
from asset_core.asset.asset_diff import AssetDiff
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import colored_string, LogColors
from asset_utils.utils.progress import Progress
from .repo import RepoAPI


class SwitchAssetAPI(RepoAPI):
    """API for switching the current version of an asset to another version.
    """

    def run(self, args):
        pass

    def switch_to_latest(self, force=False) -> bool:
        """Switches the current asset to the latest version.

        Parameters
        ----------
        force : bool, optional
            Whether to force the switch without asking the user for confirmation, by default False.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        latest_version = AssetFetcher(store=self.store).get_version_from_bucket(class_id=self.asset.asset_class.id,
                                                                                seq_id=str(self.asset.seq_id))
        if not latest_version:
            raise exceptions.AssetNotFoundError(f"can not find version data for asset: {self.asset.name}")
        self.user_log.info(f"latest version of asset: {self.asset.name} is: {latest_version.get('number')}")

        if self.asset.version.number == latest_version.get('number'):
            self.user_log.info("latest version is already active, nothing to pull")
            return True

        return self.switch_to_version(ver_number=latest_version.get('number'), ask_confirmation=not force)

    def switch_to_version(self, ver_number: str, ask_confirmation=True) -> bool:
        """Switches the current asset to a specified version.

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

        Raises
        ------
        exceptions.AssetException
            If an error occurs during the switch process.
        """
        try:
            prev_asset = self.asset
            if prev_asset.version.number == ver_number:
                self.user_log.info(f"asset: {prev_asset.name}, version: {prev_asset.version.number} is already active")
                return True

            if not self.can_switch_version(prev_asset, ask_confirmation=ask_confirmation):
                return False

            # create version meta data
            pbar = Progress.status_bar(desc=f"creating meta information for version: {ver_number}")
            manifest_file = AssetDiff().create_asset_manifest(
                repo=self.asset.repo,
                asset_name=self.asset.name,
                ver_number=ver_number
            )
            asset = Asset(repo=self.asset.repo, id=self.asset.id, load=False)
            asset.de_serialize(data=FileUtils.read_json(manifest_file))
            asset.set_as_current()
            pbar.close(message="done")

            fetcher = AssetFetcher(store=asset.repo.store)
            fetcher.download_contents(contents=asset.contents)

            # unlink the existing asset
            pbar = Progress.progress_bar(total=len(prev_asset.objects),
                                         desc=f"unlinking files for previous version: {prev_asset.version.number}")
            prev_asset.objects.unlink(callback=lambda x: pbar.update(1))
            pbar.close("done")

            # link the new asset
            pbar = Progress.progress_bar(total=len(asset.objects), desc=f"linking files for version: {ver_number}")
            asset.objects.link(callback=lambda x: pbar.update(1))
            pbar.close("done")

            message = colored_string("Success\n", LogColors.SUCCESS)
            message += colored_string(f"asset: {asset.name}, version: {asset.version.number} is now active",
                                      LogColors.INFO)
            self.user_log.message(message)
            return True

        except exceptions.AssetException as e:
            if type(e) is exceptions.InvalidAssetNameError:
                e.logs.add("invalid asset name", LogColors.ERROR)
            elif type(e) is exceptions.AssetNotFoundError:
                e.logs.add("asset not found locally\n", LogColors.INFO)
                e.logs.add(f"{UserCommands().fetch_assets()}")
            elif type(e) is exceptions.InvalidVersionError:
                e.logs.add(f"invalid version, {ver_number} not found in asset:{self.asset.name}\n",
                           LogColors.ERROR)
                e.logs.add(UserCommands().list_versions())
            raise

    def can_switch_version(self, asset, ask_confirmation=True):
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
            self.print_unstaged_changes(changes=unstaged_changes)
            return self.should_proceed_version_switch(ask_confirmation=ask_confirmation)

        return True

    def should_proceed_version_switch(self, ask_confirmation=True):
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

    def print_unstaged_changes(self, changes: dict):
        """Prints a list of unstaged changes to the user.

        Parameters
        ----------
        changes : dict
            A dictionary containing lists of 'deleted' and 'modified' files.
        """
        color = LogColors.red
        self.user_log.info(
            "you have unstaged changes to the current version, if you switch, you will lose these changes")

        columns = {
            "section": "",
            "details": "",
        }

        data = []
        if changes.get("deleted"):
            data += [{"section": colored_string("deleted: ", color), "details": colored_string(obj.path, color)}
                     for obj in changes.get("deleted")]

        if changes.get("modified"):
            data += [{"section": colored_string("modified: ", color), "details": colored_string(obj.path, color)}
                     for obj in changes.get("modified")]

        self.user_log.table(columns=columns, rows=data, table_fmt="plain")
