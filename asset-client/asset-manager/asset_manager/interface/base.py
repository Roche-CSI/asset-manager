import abc

from asset_core.configs import AppSettings
from asset_core.store import Repo, AssetStore
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import LoggingMixin, LogColors


class BaseInterface(LoggingMixin, metaclass=abc.ABCMeta):
    requires_auth = True
    requires_repo = True
    requires_store = True

    def execute(self, args):
        if self.requires_auth and (not self.user or not self.user.get("id")):
            self.user_log.message(self.auth_error())
            return

        if self.requires_store and not self.asset_store:
            self.user_log.message(self.store_error())
            return

        if self.requires_repo and not self.repo:
            self.user_log.message(self.repo_error())
            return

        self.run(args=args)

    def repo_error(self):
        """subclass can override to return custom message"""
        message = self.user_log.colorize("you are not inside an asset directory\n", color=LogColors.ERROR)
        message += f"{UserCommands().create_asset()}\n"
        message += UserCommands().clone_asset()
        return message

    def store_error(self):
        """subclass can override to return custom message"""
        message = self.user_log.colorize("asset store missing, you must create a store in order to fetch assets\n",
                                         color=LogColors.ERROR)
        return message

    def auth_error(self):
        """subclass can override to return custom message"""
        message = self.user_log.colorize("you are not signed in\n", color=LogColors.ERROR)
        message += f"{UserCommands().user_login()}\n"
        return message

    @abc.abstractmethod
    def run(self, args):
        raise NotImplementedError

    @property
    def user(self):
        return AppSettings.shared().user

    @property
    def repo(self):
        try:
            return Repo()
        except exceptions.NotAssetRepoError:
            if self.requires_repo:
                self.user_log.info("outside asset repo")
            return None
        except exceptions.InvalidCredentialError as e:
            self.user_log.error(e.msg)
            return None

    @property
    def asset_store(self):
        try:
            return AssetStore.shared()
        except exceptions.AssetStoreInvalidError:
            # invalid store so try to create
            self.user_log.message("asset store not found, creating...", )
            try:
                AssetStore.create_store()
            except exceptions.AssetStoreCreateError as e:
                msg = self.user_log.colorize(f"{str(e)}\n", color=LogColors.ERROR)
                msg += self.user_log.colorize("in order to work, asset-manager needs a ASSET_HOME directory\n",
                                              LogColors.INFO)
                msg += f"to set ASSET_HOME: {UserCommands().set_asset_store()}"
                self.user_log.message(msg)

            store = AssetStore.shared()
            msg = self.user_log.colorize("Success\n", LogColors.SUCCESS)
            msg += self.user_log.colorize(f"created asset store at:{store.home_dir}", LogColors.INFO)
            self.user_log.message(msg)
            return store
