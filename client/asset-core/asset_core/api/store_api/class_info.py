import os.path

from asset_core.asset.asset_class import AssetClass
from asset_core.configs import AppSettings, Configs
from asset_core.store import AssetStore
from asset_utils.common import exceptions
from asset_utils.common.user_commands import UserCommands
from asset_utils.utils.log_utils import LogColors
from asset_utils.utils.web_utils import open_in_browser
from .store import StoreAPI


class ClassInfoAPI(StoreAPI):

    def create_asset_class(self):
        create_route = "asset_class?action=create&project_id={project_id}"
        url = os.path.join(Configs.shared().asset_home.dashboard_url,
                           create_route.format(project_id=self.store.project_id))
        self.user_log.info("opening asset-create page in dashboard")
        open_in_browser(url)

    def print_class_info(self, class_name, project_id=None, jsonize=False):
        if not class_name:
            raise exceptions.AssetException("No current asset-class found")

        if project_id and self.store.project_id != project_id:
            AppSettings.shared().set_project_environment(project_id=project_id)

        store = AssetStore.shared()
        asset_class = AssetClass(name=class_name,
                                 store=store,
                                 project=store.project_id)
        try:
            data = asset_class.cached_class_data(store=store, name=class_name)
            data["project"] = AppSettings.shared().projects.get(data.get("project")).get("name")
            keys = ["name", "id", "created_at", "created_by", "class_type", "project"]
            data = {key: data[key] for key in keys}
        except exceptions.AssetClassNotFoundError as e:
            message = "make sure the correct project is activated\n"
            message += "\n".join([UserCommands().activate_project(), UserCommands().list_projects()])
            e.logs.add(message, LogColors.INFO)
            raise
        except exceptions.ClassListNotFoundError as e:
            message = "\n".join([UserCommands().fetch_assets(), UserCommands().fetch_classes()])
            e.logs.add(message, LogColors.INFO)
            raise

        if jsonize:
            return data

        self.print_asset_class(class_data=data)

    def print_asset_class(self, class_data):
        columns = {
            "section": "",
            "details": "",
        }
        data = [
            {"section": "class name: ", "details": class_data.get("name")},
            {"section": "id: ", "details": class_data.get("id")},
            {"section": "project: ", "details": class_data.get("project")},
            {"section": "created_by: ", "details": class_data.get("created_by")},
            {"section": "created_at: ", "details": class_data.get("created_at")},
            {"section": "type: ", "details": class_data.get("class_type")},
        ]
        self.user_log.table(columns=columns, rows=data, table_fmt="simple")
