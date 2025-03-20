from asset_core.asset.asset_class import AssetClass
from asset_core.asset.fetchers.asset_fetcher import AssetFetcher
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import colored_string, LogColors
from .store import StoreAPI

DEFAULT_VERSION_WINDOW_SIZE = 50


class FetchAPI(StoreAPI):

    def run(self, args):
        pass

    def fetch_asset(self, asset_name, force=False):
        AssetFetcher(store=self.store).download_asset(asset_name=asset_name, force=force)
        message = colored_string("\nCompleted\n", LogColors.SUCCESS)
        message += f"{UserCommands().asset_info()}\n"
        message += UserCommands().list_assets()
        self.user_log.message(message)

    def fetch_all(self, force=False):
        self.fetch_classes(force=force)
        classes = AssetClass.list_classes(store=self.store)
        for class_name in classes:
            self.fetch_assets(class_name, force=force)

    def fetch_classes(self, force=False):
        """fetch all classes meta-data from bucket
        The classes meta file is asset-classes.yaml
        """
        self.user_log.message(f"fetching asset-classes from remote: {self.store.asset_classes_url}",
                              color=LogColors.INFO)
        AssetFetcher(store=self.store).download_asset_classes(force=force, show_progress=True)
        self.user_log.message("\ncompleted", color=LogColors.SUCCESS)
        self.user_log.message(f"to view the list of classes: {UserCommands().list_classes()}")
        return True

    def fetch_assets(self, class_name, force=False):
        if not class_name:
            self.user_log.message("did you forget set the current class")
            self.user_log.message("use: asset class use <name> to set the current class before calling fetch")
        self.user_log.message(f"fetching assets for class: {class_name}")
        class_id = AssetClass.get_id(store=self.store, name=class_name)
        fetcher = AssetFetcher(store=self.store)
        if not class_id:
            # we need to fetch class list again
            fetcher.download_class_list(force=force)
            class_id = AssetClass.get_id(store=self.store, name=class_name)
        if not class_id:
            # typo or non-existing asset_class
            self.user_log.message(f"invalid class-name, no asset-class found for name:{class_name}")
            self.user_log.message("to create an asset class, use the command: asset class init <name>")
            self.user_log.message("to upload an asset class, use the command: asset class upload <name>")
            return

        targets = fetcher.download_assets_for_class(class_id=class_id,
                                                    show_progress=True,
                                                    force=force)
        if targets:
            msg = f"completed - fetched asset list from remote for class: {class_name}"
        else:
            msg = "asset list is already up to date"
        self.user_log.success(msg)
        self.user_log.message(UserCommands().list_assets())

    def fetch_versions(self, asset_data: dict):
        fetcher = AssetFetcher(store=self.store)
        fetcher.download_window_versions(class_id=asset_data['asset_class']['id'],
                                         seq_id=asset_data['seq_id'],
                                         target_version=asset_data['version']['number'],
                                         window_size=DEFAULT_VERSION_WINDOW_SIZE)
        fetcher.download_asset_objects(class_id=asset_data['asset_class']['id'],
                                       seq_id=asset_data['seq_id'])
        self.user_log.message(UserCommands().list_versions())
