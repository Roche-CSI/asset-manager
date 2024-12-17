import os

from asset_core.objects import Object
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.log_utils import colored_string, LogColors
from .repo import RepoAPI


class DiscardAPI(RepoAPI):
    """discards uncommitted assets"""

    def discard_all_changes(self, ask_user=True):
        """discards all local changes to an asset and restores it back to its previous
        committed version
        """
        if self.asset.is_temp:
            self.discard_temp_asset(ask_user=ask_user)
        else:
            self.discard_committed_asset(ask_user=ask_user)

    def discard_committed_asset(self, ask_user=True):
        msg = "this will remove all staged changes to the asset, do you wish to continue?"
        user_input = self.user_log.ask_user(question=msg, options=["y", "n"],
                                            default="y", ask_confirmation=ask_user)
        if user_input.lower() == "y":
            self.asset.objects.unlink()
            os.remove(self.asset.manifest_file)
            FileUtils.clone_file(src=self.asset.cached_manifest_file, dst=self.asset.manifest_file)
            # de_serialize to relink
            self.asset.de_serialize()
            self.asset.objects.link()

            msg = colored_string("Completed\n", LogColors.SUCCESS)
            msg += "your local changes have been discarded\n"
            msg += UserCommands().asset_info()
        else:
            msg = colored_string("aborted\n", LogColors.INFO)
            msg += UserCommands().asset_info()
        self.user_log.message(msg)

    def discard_temp_asset(self, ask_user=True):
        msg = "this is an uncommitted asset, please choose: \n"
        msg += "1 delete the asset\n"
        msg += "2 keep the asset but remove any changes I made\n"
        self.user_log.message(msg)
        user_input = self.user_log.ask_user(question="please select an option", options=["1", "2"],
                                            default="1", ask_confirmation=ask_user)
        status = ""
        if user_input == "1":
            # if asset id is the current asset, reset the current asset
            if self.asset.id == self.asset.repo.current_asset.get("id"):
                self.asset.repo.current_asset = None

                # remove from temp assets list
                # store the name for logging before we remove
                asset_name = self.asset.name
                self.asset.repo.remove_from_temp_assets(seq_id=self.asset.seq_id,
                                                        class_name=self.asset.asset_class.name)
                status = colored_string(f"asset: {asset_name} deleted \n", LogColors.INFO)
                FileUtils.delete_file(self.asset.manifest_file)
                FileUtils.delete_file(self.asset.states_file)
        elif user_input == "2":
            # remove objects
            self.asset.remove_objects(list(self.asset.objects))
            self.asset.refs = []
            self.asset.alias = None
            status = f"all changes to asset: {self.asset.name} have been discarded\n"
            status += "asset is clean\n"
            status = colored_string(status, LogColors.INFO)
        else:
            self.user_log.error("invalid response")
            return

        message = "Completed\n"
        message += status

        self.user_log.success(message)

    def discard_unstaged_files(self, targets):
        """discards all unstaged changes to an object"""
        found = self._get_objects(targets)
        if not found:
            return

        for object in found:
            edit_status = object.edit_status()
            if edit_status in [Object.edit_statuses.MODIFIED, Object.edit_statuses.DELETED]:
                # relink, this will restore from cache and all changes will be gone
                object.link_from_store()

        message = colored_string("Success\n", LogColors.SUCCESS)
        message += "restored the following files in the asset:\n"
        message += "\n".join([os.path.relpath(obj.linked_path, self.asset.repo.fs_path)
                              for obj in found])
        self.user_log.message(message)

    def discard_staged_files(self, targets):
        found = self._get_objects(targets)
        if not found:
            return

        # temporary asset, so no history to revert back to
        # we just remove all objects
        if self.asset.is_temp:
            self.asset.objects.clear()
            self.user_log.message("discarded all local changes")
            return

        # if it's a committed asset, we check if the files are additions or removals
        # if they are additions i.e. new  files, we simply remove those
        # if they are removals or modifications, we add back the old object and link

        cached_manifest = self.asset.cached_manifest_data()
        cached_objects = {Object.parse_id(object.get("id"))[1]: object
                          for object in cached_manifest.get("objects", [])}

        to_be_added = []
        to_be_removed = []
        for obj in found:
            if obj.path in cached_objects:
                # either removal or modification
                new_object = Object.de_serialize(asset=self.asset,
                                                 data=cached_objects[obj.path])
                to_be_added.append(new_object)
            else:
                to_be_removed.append(obj)

        # add back
        self.asset.add_objects(to_be_added)
        # remove
        self.asset.remove_objects(to_be_removed)

        message = colored_string("Success\n", LogColors.SUCCESS)
        message += colored_string("discarded staged changes for file(s) specified", LogColors.INFO)
        self.user_log.message(message)

    def _get_objects(self, targets):
        if not targets:
            message = colored_string("missing required param <file>, did you miss to include file path?\n",
                                     LogColors.ERROR)
            self.user_log.message(message)
            return []

        found = self.asset.objects.find(targets)
        if not found:
            message = "file not found in the asset, make sure the file path is correct"
            self.user_log.message(message, LogColors.INFO)
            return []
        return found
