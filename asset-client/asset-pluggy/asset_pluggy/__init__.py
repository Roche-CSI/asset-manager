from asset_pluggy.plugin.plugin_manager import PluginManager


def register_plugins(*args):
    plm = PluginManager.shared()
    for plugin_klass in args:
        plm.register(plugin=plugin_klass())
