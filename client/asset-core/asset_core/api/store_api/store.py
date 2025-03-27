from asset_core.api.base_api import BaseAPI
from asset_core.configs import AppSettings
from asset_core.store import Repo


class StoreAPI(BaseAPI):
    repo: Repo = None

    def __init__(self, store=None, repo=None):
        super().__init__(store=store)
        self.repo = repo

    def set_environment(self):
        AppSettings.shared().set_project_environment(project_id=AppSettings.shared().active_project)

    def unset_environment(self):
        AppSettings.shared().unset_project_environment()
