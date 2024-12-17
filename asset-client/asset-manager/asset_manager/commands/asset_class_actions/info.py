from asset_core.api.store_api import ClassInfoAPI
from asset_manager.commands import CliAction, CliOption


class AssetClassInfo(CliAction):
    name = "info"
    help_msg = "prints information on the asset class"
    requires_repo = False

    def run(self, args):
        project_id = None
        if args.class_name:
            class_name = args.class_name
        elif self.repo:
            class_name = self.repo.current_asset.get("asset_class").get("name")
            project_id = self.repo.current_asset.get("asset_class").get("project")
        else:
            self.user_log.error("You are not inside an asset repo. Please specify an asset-class name.")
            return
        api = ClassInfoAPI(store=self.asset_store)
        with api.environment():
            api.print_class_info(class_name=class_name, project_id=project_id)

    def get_options(self):
        return [
            CliOption(dest="class_name",
                      help_msg="enter the asset-class name you want to print information for",
                      short_name="n",
                      full_name="name"
                      ),
        ]
