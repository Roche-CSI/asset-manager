import os

from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils import LogColors
from asset_utils.utils.log_utils import colored_string
from .add import AddAPI
from .repo import RepoAPI


class UpdateAPI(RepoAPI):
    """Update Asset adds the untracked changes to asset. For details of untracked changes
    see StatusAPI.
    Updating the asset involves:
     - if file is deleted, then we remove it from asset
     - if file is modified then we re add the file
    """

    def update_asset(self, prompt_user: bool):
        self._update(objects=self.asset.objects, prompt_user=prompt_user)

    def update_objects(self, targets: [str], prompt_user: bool):
        """updates un-staged changes to an object

        Parameters
        ----------
        targets: list.
                 list of file paths.
        """
        if not targets:
            message = colored_string("missing required param <file>, did you miss to include file path?\n",
                                     LogColors.ALERT)
            message += f"to update files: {UserCommands().update_asset()}"
            self.user_log.message(message)
            return

        found = self.asset.objects.find(targets)
        self._update(objects=found, prompt_user=prompt_user)

    def _update(self, objects, prompt_user: bool):
        # check linking type
        if self.asset.repo.linking_type != "copy":
            raise exceptions.ReadOnlyAssetError(
                f"read-only asset, change tracking and updates are disabled: {self.asset.repo.linking_type}")

        if not objects:
            message = "not found in the asset, make sure the file path is correct"
            self.user_log.message(message, LogColors.INFO)
            return

        deleted = []
        modified = []
        for obj in objects:
            edit_status = obj.edit_status()
            if edit_status == obj.edit_statuses.DELETED:
                deleted.append(obj)
            elif edit_status == obj.edit_statuses.MODIFIED:
                modified.append(obj)

        if not deleted and not modified:
            self.user_log.message("no unstaged changes found")
            return

        if deleted:
            self.asset.remove_objects(deleted)
            message = "removed the following files from asset:\n"
            message += "\n".join([os.path.relpath(obj.linked_path, self.asset.repo.fs_path)
                                  for obj in deleted])
            self.user_log.message(message)
        if modified:
            AddAPI(repo=self.repo).add_files(targets=[obj.linked_path for obj in modified],
                                             prompt_user=prompt_user,
                                             mode="update")
            # message = "updated the following files in the asset:\n"
            # message += "\n".join([os.path.relpath(obj.linked_path, self.asset.repo.fs_path)
            #                       for obj in modified])
            # self.user_log.message(message)
