from asset_pluggy.plugin.plugin_manager import PluginManager

from asset_plugin_gcs import GcsStoragePlugin
from asset_plugin_s3 import AwsStoragePlugin

BUNDLED_PLUGINS = [
    GcsStoragePlugin,
    AwsStoragePlugin,
]


def register_plugins():
    plm = PluginManager.shared()
    for plugin_klass in BUNDLED_PLUGINS:
        plm.register(plugin=plugin_klass())
