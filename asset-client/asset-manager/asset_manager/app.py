import sys

from asset_core.configs import configs
from asset_manager.arg_parse import get_parser
from asset_manager.plugins import register_plugins

# change to ConfigModes.PRODUCTION for asset-manager
# change to ConfigModes.USER_TEST for asset-sandbox
ACTIVE_CONFIG_MODE = configs.ConfigModes.USER_TEST


def run():
    register_plugins()
    get_parser(mode=ACTIVE_CONFIG_MODE).run(sys.argv[1:])


if __name__ == '__main__':
    run()
