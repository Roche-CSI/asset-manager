from asset_core.api.base_api import BaseAPI
from asset_core.asset import Asset
from asset_core.configs import AppSettings
from asset_core.store.repo import Repo


class RepoAPI(BaseAPI):
    repo: Repo = None
    view: Asset.views = None
    load_asset: bool = True

    def __init__(self, repo=None, asset=None):
        super().__init__(store=repo.store if repo else None)
        self.repo = repo
        self.view = Asset.views.DATA  # default to data
        if asset:
            if asset.view == self.view:
                setattr(self, "_asset", asset)
                if not self.repo:
                    self.repo = asset.repo
            else:
                raise Exception("asset view doesn't match with api view")

    @property
    def asset(self) -> Asset:
        if not hasattr(self, "_asset"):
            setattr(self, "_asset", Asset(self.repo,
                                          load=self.load_asset,
                                          view=self.view) if self.repo else None)
        return getattr(self, "_asset")

    @property
    def project_id(self):
        if not hasattr(self, "_project_id"):
            # avoid loading the whole asset, we just need the project-id
            asset = Asset(repo=self.repo, load=False)
            setattr(self, "_project_id", asset.project_id)
        return getattr(self, "_project_id")

    def set_environment(self):
        AppSettings.shared().set_project_environment(project_id=self.project_id)

    def unset_environment(self):
        AppSettings.shared().unset_project_environment()
