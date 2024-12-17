import abc

from asset_core.configs import AppSettings
from asset_core.store import Repo, AssetStore
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import LoggingMixin, colored_string, LogColors


class BaseAction(LoggingMixin):
    requires_auth = True
    requires_repo = True
    requires_store = True

    def execute(self, args):
        self.run_with_exception(args=args)

    def can_run(self) -> bool:
        if self.requires_auth and (not self.user or not self.user.get("id")):
            self.user_log.message(self.auth_error())
            return False
        if self.requires_store and not self.asset_store:
            self.user_log.message(self.store_error())
            return False
        if self.requires_repo and not self.repo:
            self.user_log.message(self.repo_error())
            return False
        return True

    def run_with_exception(self, args):
        try:
            if self.can_run():
                self.run(args)
        except exceptions.AssetException as e:
            self.user_log.message(e.msg, LogColors.ERROR)
            self.user_log.message(e.logs.print_format())
            e.stop_execution()

    def repo_error(self):
        """subclass can override to return custom message"""
        message = colored_string("you are not inside an asset directory\n", color=LogColors.ERROR)
        message += f"{UserCommands().create_asset()}\n"
        message += UserCommands().clone_asset()
        return message

    def store_error(self):
        """subclass can override to return custom message"""
        message = colored_string("asset store missing, you must create a store in order to fetch assets\n",
                                 color=LogColors.ERROR)
        return message

    def auth_error(self):
        """subclass can override to return custom message"""
        message = colored_string("you are not signed in\n", color=LogColors.ERROR)
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
        except exceptions.NotAssetRepoError as e:
            if self.requires_repo:
                e.logs.add("outside asset repo", LogColors.ERROR)
                raise
            return None

    @property
    def asset_store(self):
        return AssetStore.shared(create_if_not_exists=True)
