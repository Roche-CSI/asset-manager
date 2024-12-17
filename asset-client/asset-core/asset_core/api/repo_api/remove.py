import os

from asset_utils.utils import cast2list, list_files, relative_path
from asset_utils.utils.log_utils import colored_string, LogColors
from .info import InfoAPI
from .repo import RepoAPI


class RemoveAPI(RepoAPI):

    def remove_alias(self):
        raise NotImplementedError

    def remove_refs(self, targets):
        """
        Parameters
        ----------
        targets: [str]
            asset version names to remove from refs
        """
        if not targets:
            self.user_log.message("nothing to remove, did you forget to pass <asset_version_name>")
            return
        targets: list = cast2list(targets)
        to_remove = self.asset.refs.filter(predicate=lambda x: x.src_version.get("name") in targets)
        if to_remove:
            self.asset.remove_refs(to_remove)
            self.user_log.success("completed")
            self.user_log.alert(f"input(s) pending for removal: {', '.join(targets)}\n")
            InfoAPI(self.repo).list_refs()
        else:
            self.user_log.info(f"{', '.join(targets)} not found, nothing to remove")

    def remove_files(self, targets, prompt_user):
        """ removes a file or directory from assets
        Parameters
        ----------
        targets: list of dirs or files
        prompt_user: bool

        Returns
        -------
        """
        to_remove = []
        # list files
        for target in cast2list(targets):
            files = list_files(root_dir=target) if os.path.isdir(target) else cast2list(target)
            to_remove += [relative_path(os.path.abspath(file), self.asset.repo.fs_path) for file in files]

        # get the objects corresponding to files and remove
        # find the objects, its possible the user might call remove again on a already removed file
        objs = self.asset.objects.filter(predicate=lambda x: x.path in to_remove)

        if objs:
            # ask user to confirm
            msg = f"this will remove {len(objs)} files from the asset, do you wish to continue?"
            proceed = True
            if prompt_user:
                user_input: str = self.user_log.ask_user(question=msg, options=["y", "n"], default="y")
                proceed = bool(user_input.lower() == "y")
            if proceed:
                self.asset.remove_objects(objs)
                rel_paths = [os.path.relpath(obj.linked_path, os.getcwd()) for obj in objs]
                msg = colored_string("completed\n", LogColors.SUCCESS)
                msg += colored_string(f"{len(rel_paths)} files removed from asset\n", LogColors.ALERT)
                msg += "\n".join(rel_paths)
            else:
                msg = colored_string("remove aborted", LogColors.INFO)

        else:
            msg = colored_string(f"{targets} not found in asset, nothing to remove", LogColors.INFO)

        self.user_log.message(msg)
