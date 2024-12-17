from asset_core.asset.asset_diff import AssetDiff
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors, bold_string
from .repo import RepoAPI


class StatusAPI(RepoAPI):
    """Asset status displays the following
    1. changes to asset made by the user from previous commit, these could be
        - files added,
        - files removed
    2. files altered, i.e. changes by the user to files, that have not been updated in the asset
       - user downloads the asset, then deletes a file / files
       - user modifies the contents of the file
       - user renames a file / files
    3. untracked files, i.e. files that are not part of the asset
       - user adds new files to the asset

    For changes in (2), we need to inform the user that they need to update the asset
    otherwise those changes will not be pushed to remote
    For changes in (3), we need to inform the user that they need to add the files to the asset
    """

    def display_status(self, jsonize=False):
        """Display the status of the asset.

        Parameters
        ----------
        jsonize : bool, optional
            Whether to return the data in JSON format, by default False.

        Returns
        -------
        dict or None
            The status data if jsonize is True, otherwise None.
        """
        differ = AssetDiff()
        data = self.print_patch_table(staged=differ.staged_changes(asset=self.asset),
                                      unstaged=differ.unstaged_changes(asset=self.asset),
                                      untracked=differ.untracked_changes(asset=self.asset),
                                      jsonize=jsonize)
        if jsonize:
            return data

        if not data:
            message = colored_string(f"asset: {self.asset.name}\n", LogColors.INFO)
            message += f"version: {self.asset.version.number}\n"
            message += colored_string("asset is clean, there are no changes", LogColors.ACTIVE)
            self.user_log.message(message)

    def print_patch_table(self, staged: dict,
                          unstaged: dict,
                          untracked: dict,
                          jsonize=False):
        """Print the patch table.

        Parameters
        ----------
        staged : dict
            The staged changes.
        unstaged : dict
            The unstaged changes.
        untracked : dict
            The untracked changes.
        jsonize : bool, optional
            Whether to return the data in JSON format, by default False.

        Returns
        -------
        bool or dict
            False if there are no changes, True if there are changes.
            Otherwise, the changes data if jsonize is True.
        """
        if not staged and not unstaged and not untracked and not jsonize:
            return False

        # check linking type
        if self.asset.repo.linking_type != "copy":
            raise exceptions.ReadOnlyAssetError(
                f"read-only asset, change tracking and updates are disabled: {self.asset.repo.linking_type}")

        if jsonize:
            return {
                "asset": self.asset.name,
                "version": self.asset.version.number,
                "staged_changes": staged,
                "unstaged_changes": unstaged,
                "untracked_changes": untracked
            }

        title = f"asset: {self.asset.name}\n"
        title += f"version: {self.asset.version.number}"
        self.user_log.message(title)

        columns = {
            "section": "",
            "details": "",
        }

        if staged:
            color = LogColors.ACTIVE
            header = bold_string("\nChanges to be committed:")
            tr_table = []
            if staged.get("added"):
                tr_table += [{"section": colored_string("added: ", color),
                              "details": colored_string(obj, color)}
                             for obj in staged.get("added")]
            if staged.get("removed"):
                tr_table += [{"section": colored_string("removed: ", color),
                              "details": colored_string(obj, color)}
                             for obj in staged.get("removed")]
            if staged.get("altered"):
                tr_table += [{"section": colored_string("modified: ", color),
                              "details": colored_string(obj, color)}
                             for obj in staged.get("altered")]
            self.user_log.message(header)
            self.user_log.message(f"\t{UserCommands().discard_staged_object()}")
            self.user_log.table(columns=columns, rows=tr_table, table_fmt="plain", indent=2)

        if unstaged:
            color = LogColors.ALERT
            header = bold_string("\nChanges not staged for commit:")
            utr_table = []
            if unstaged.get("deleted"):
                utr_table += [{"section": colored_string("deleted: ", color),
                               "details": colored_string(obj.path, color)}
                              for obj in unstaged.get("deleted")]

            if unstaged.get("modified"):
                utr_table += [{"section": colored_string("modified: ", color),
                               "details": colored_string(obj.path, color)}
                              for obj in unstaged.get("modified")]
            self.user_log.message(header)
            self.user_log.message(f"\t{UserCommands().discard_unstaged_object()}")
            self.user_log.message(f"\t{UserCommands().update_object()}")
            self.user_log.message(f"\t{UserCommands().update_asset()}")
            self.user_log.table(columns=columns, rows=utr_table, table_fmt="plain", indent=2)

        if untracked:
            color = LogColors.ALERT
            header = bold_string("\nUntracked files:")
            new_table = [{"section": colored_string("new: ", color),
                          "details": colored_string(file, color)}
                         for file in untracked.get("added")]
            self.user_log.message(header)
            self.user_log.message(f"\t{UserCommands().add_to_asset()}")
            self.user_log.table(columns=columns, rows=new_table, table_fmt="plain", indent=2)

        # display footer
        footer = "\n".join([
            UserCommands().discard_asset(),
        ])
        self.user_log.message(f"\n{footer}")
        return True
