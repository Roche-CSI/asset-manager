import pluggy

from asset_pluggy.plugin import APP_NAME
from asset_pluggy.plugin import specs as plugin_specs
from asset_utils.common.singleton import Singleton


class PluginManager(Singleton):

    def post_init(self):
        self._manager = pluggy.PluginManager(APP_NAME)
        for plugin in plugin_specs.__all__:
            self._manager.add_hookspecs(plugin)
        self._manager.load_setuptools_entrypoints(APP_NAME)

    @property
    def hook(self):
        return self._manager.hook

    def register(self, plugin):
        self._manager.register(plugin)
