import os

from asset_pluggy import register_plugins as pluggy
from asset_plugin_gcr import GcrStoragePlugin
from asset_plugin_gcs import GcsStoragePlugin
from asset_plugin_posix import PosixStoragePlugin
from asset_plugin_s3 import AwsStoragePlugin

BUNDLED_PLUGINS = [
    GcsStoragePlugin,
    GcrStoragePlugin,
    AwsStoragePlugin,
    PosixStoragePlugin
]

PLUGINS_REGISTERED = False


def register_plugins(env_vars=None):
    """Register all the plugins and sets the necessary environment variables"""
    if env_vars:
        for key, value in env_vars.items():
            if value:
                os.environ[key] = value

    global PLUGINS_REGISTERED
    if not PLUGINS_REGISTERED:
        pluggy(*BUNDLED_PLUGINS)
        PLUGINS_REGISTERED = True
