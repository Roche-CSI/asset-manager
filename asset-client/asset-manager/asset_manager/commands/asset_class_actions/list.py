import cached_property

from asset_core.api.store_api.list import ListAPI
from asset_manager.commands import CliAction


class ListAssetClass(CliAction):
    name = "list"
    help_msg = "Lists asset-classes in the active project"
    requires_repo = False

    def run(self, args):
        api = ListAPI(store=self.asset_store, repo=self.repo)
        with api.environment():
            api.list_classes()

    def get_options(self):
        return []

    @cached_property.cached_property
    def api(self):
        return ListAPI(store=self.asset_store, repo=self.repo)
