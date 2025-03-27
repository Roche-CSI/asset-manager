import os

from asset_core.asset import Asset, AssetClass
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_core.configs import AppSettings, Configs
from asset_core.store import AssetStore, Repo
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils import user_home_dir
from asset_utils.utils.log_utils import colored_string, LogColors, asset_logo
from asset_utils.utils.log_utils import format_link
from .repo import RepoAPI


class InitAssetAPI(RepoAPI):

    def set_environment(self):
        AppSettings.shared().set_project_environment(project_id=AppSettings.shared().active_project)

    def create_asset(self, class_name: str, location: str = None):
        """Create a new asset in the specified location.

        We need to do 3 checks to ensure that the target dir is not violating the nested asset rule
        1. the target directory is inside an asset repo. violates nested asset rule.
        2. the target directory contains an asset as a child. violates nested asset rule.
        3. the target directory itself is an asset repo (contains .asset).
        """
        try:
            class_id = self.verify_asset_class(class_name=class_name, store=AssetStore.shared())
            repo, did_create = self.create_repo(location=location)
        except exceptions.AssetClassNotFoundError as e:
            e.logs.add(UserCommands().create_asset_class())
            raise
        except exceptions.NestedRepoError as e:
            # Case 1 or 2: violation of nested asset rule, cannot create asset
            e.msg = f"Unable to initialize, {e.msg}"
            e.logs.add(colored_string(f"{e.data.get('repo')}", LogColors.INFO))
            e.logs.add("Please select a different location")
            raise

        if not did_create:
            # Case 3: the target directory has an existing asset, did not create new repo
            e = exceptions.DuplicateRepoError()
            if repo:
                asset_name = os.path.join(repo.current_asset['asset_class']['name'],
                                          str(repo.current_asset['seq_id']))
                e.msg = f"Unable to initialize, found existing asset: {asset_name}"
                e.logs.add(colored_string(f"{repo.fs_path}", LogColors.INFO))
            else:
                # this block should not be reached
                e.msg = "Unable to initialize the asset"
                e.logs.add(colored_string(f"{location or os.curdir}", LogColors.INFO))

            e.logs.add("Please select a different location")
            raise e

        # repo created successfully, initialize new asset
        asset = Asset.create_new(repo=repo, class_id=class_id, class_name=class_name)
        message = asset_logo() + "\n"
        message += f"New asset for class '{asset.asset_class.name}' initialized\n"
        message += f"asset location: {repo.fs_path}"
        self.user_log.boxed(message=message, border_color=LogColors.INFO)
        self.user_log.message(self.url_information())
        return repo.fs_path

    def verify_asset_class(self, class_name, store: AssetStore) -> str:
        """Returns the asset-class id if the class exists"""
        # check if asset-class is created, if not ask user to create through dashboard
        class_list: dict = AssetClass.active_classes(store=store)
        if class_name not in class_list:
            # fetch from remote
            self.user_log.message(f"asset-class:{class_name} not found locally, checking in remote")
            AssetFetcher(store=store).download_asset_classes(force=False, show_progress=True)
            class_list = AssetClass.active_classes(store=store)
        class_id = class_list.get(class_name)
        if not class_id:
            raise exceptions.AssetClassNotFoundError(f"class not found:{class_name}")
        return class_id

    def create_repo(self, location: str = None) -> (Repo, bool):
        """Create a new repo if it doesn't exist

        Parameters
        ----------
        location : str
            location to create the repo

        Returns
        -------
        Repo
            the repo object
        bool
            whether the repo was created or not
        """
        repo_dir = os.path.realpath(location) if location else os.path.realpath(os.curdir)
        try:
            did_create = False
            repo = Repo(root=repo_dir)
        except exceptions.NotAssetRepoError:
            # check if the user is creating the asset in the home directory
            if os.path.samefile(repo_dir, user_home_dir()):
                message = "initializing asset in the home directory which is not recommended, do you wish to continue?"
                user_input = self.user_log.ask_user(question=message, options=["y", "n"], default="y")
                if user_input and user_input.lower() != 'y':
                    return None, False
            # create the new repo
            repo = Repo.create_repo(root_dir=repo_dir)
            did_create = True

        return repo, did_create

    def url_information(self):
        docs_url = Configs.shared().docs_url
        issue_url = Configs.shared().issue_url
        github_url = Configs.shared().github_url
        return f"""Check out the following:
                - documentation: {format_link(docs_url)}
                - get help and share ideas: {format_link(issue_url)}
                - star us on GitHub: {format_link(github_url)}
                """
