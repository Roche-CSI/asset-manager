import os
import argparse
from asset_manager.commands.asset_actions.find import AssetFind
from asset_manager.debug_configs.store.store_debug import AssetStoreDebug


def run_asset_find(debug: AssetStoreDebug, class_name: str, alias: str, hash: str):
    args = argparse.Namespace()
    args.class_name = class_name
    args.alias = alias
    args.hash = hash
    debug.run(callable=lambda: AssetFind().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    class_name = "rnn_model"
    alias = "tandonp1_20221117_193040_9a15a7a_ckpt0_9a15a7a_6_ckpt37"
    hash = None

    debug = AssetStoreDebug(target_dir=debug_dir)
    run_asset_find(debug=debug, class_name=class_name, alias=alias, hash=hash)
