"""
app wrapper for triggering from IDE run configuration
"""
import os

from asset_core.configs.config_modes import ConfigModes
from asset_manager.app import run, get_parser
from asset_utils import common


def main():
    print("----THIS IS THE APP WRAPPER RUNNING FROM LOCAL CODEBASE----")
    if common.DEBUG:
        # temporary work around so that we can mock command line from pycharm run configurations
        args, unknown = get_parser(mode=ConfigModes.USER_TEST).parse_args()
        if unknown and unknown[0] == "--asset_dir":
            debug_dir = unknown[1]
        else:
            debug_dir = ""
        os.makedirs(debug_dir, exist_ok=True)
        os.chdir(debug_dir)

    run()


if __name__ == "__main__":
    main()
