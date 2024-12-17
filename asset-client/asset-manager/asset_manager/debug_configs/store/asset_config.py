import os
import argparse
from asset_manager.commands.config_actions.set_configs import SetConfigs
from asset_manager.debug_configs.store.store_debug import AssetStoreDebug


def run_asset_config(debug: AssetStoreDebug):
    args = argparse.Namespace()
    args.key = "dont_ask_user"
    args.value = "true"
    debug.run(callable=lambda: SetConfigs().run(args=args))


if __name__ == "__main__":
    debug = AssetStoreDebug()
    run_asset_config(debug=debug)
