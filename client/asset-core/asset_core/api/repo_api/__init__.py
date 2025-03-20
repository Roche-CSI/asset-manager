from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import LoggingMixin, LogColors, colored_string
from .add import AddAPI
from .debug import DebugAPI
from .diff import DiffApi
from .discard import DiscardAPI
from .download import DownloadAPI
from .info import InfoAPI
from .init import InitAssetAPI
from .remote import RemoteAPI
from .remove import RemoveAPI
from .report import ReportAPI
from .status import StatusAPI
from .switch import SwitchAssetAPI
from .union import UnionApi
from .update import UpdateAPI
from .upload import UploadAPI
from .version import VersionAPI
from asset_core.asset import Asset


class AssetAPI(LoggingMixin):
    repo = None

    def __init__(self, repo):
        self.repo = repo

    @property
    def add(self) -> AddAPI:
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return AddAPI(repo=self.repo)

    @property
    def upload(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return UploadAPI(repo=self.repo)

    @property
    def download(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return DownloadAPI(self.repo)

    @property
    def remove(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return RemoveAPI(self.repo)

    @property
    def remote(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return RemoteAPI(self.repo)

    @property
    def version(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return VersionAPI(self.repo)

    @property
    def status(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return StatusAPI(self.repo)

    @property
    def info(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return InfoAPI(self.repo)

    @property
    def report(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return ReportAPI(self.repo)

    @property
    def discard(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return DiscardAPI(self.repo)

    @property
    def update(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return UpdateAPI(self.repo)

    @property
    def switch(self):
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return SwitchAssetAPI(self.repo)

    @property
    def diff(self) -> DiffApi:
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return DiffApi(self.repo)

    @property
    def union(self) -> UnionApi:
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return UnionApi(self.repo)

    @property
    def debug(self) -> DebugAPI:
        if not self.repo.current_asset:
            self.asset_missing()
            return None
        return DebugAPI(self.repo)

    @property
    def init(self):
        return InitAssetAPI(repo=None)

    def asset_missing(self):
        message = colored_string("asset not found\n", LogColors.ERROR)
        message += f"{UserCommands().create_asset()}\n"
        message += f"{UserCommands().clone_asset()}\n"
        self.user_log.message(message)
