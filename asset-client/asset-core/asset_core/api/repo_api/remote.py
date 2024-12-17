from asset_core.configs import AppSettings
from asset_utils.common import exceptions
from .repo import RepoAPI


class RemoteAPI(RepoAPI):

    def print_remote(self):
        if self.asset.is_temp:
            self.user_log.message("this asset has not been uploaded yet")
            return

        columns = {
            "section": "",
            "details": "",
        }
        project: dict = AppSettings.shared().projects.get(self.asset.asset_class.project)
        if not project:
            raise exceptions.InvalidProjectError()
        data = [
            {"section": "project: ", "details": project.get("name")},
            {"section": "asset: ", "details": self.asset.name},
            {"section": "version: ", "details": self.asset.version.number or "None"},
            {"section": "meta: ", "details": self.asset.remote_url},
            {"section": "contents: ", "details": self.asset.contents.remote_url},
            {"section": "contents-staging: ", "details": self.asset.contents.staging_url},
        ]

        self.user_log.table(columns=columns, rows=data, table_fmt="plain")
