import os
import argparse
from asset_manager.commands.asset_actions.clone import CloneAsset
from asset_manager.debug_configs.store.store_debug import AssetStoreDebug


def run_asset_clone(debug: AssetStoreDebug, asset_name: str):
    args = argparse.Namespace()
    args.asset_name = asset_name
    args.r = False
    args.dir = None
    args.force = False
    args.credentials = None
    args.soft = None
    debug.run(callable=lambda: CloneAsset().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    # asset_name = "dsaswe_test/23"
    asset_name = "v2_objects/10"
    debug = AssetStoreDebug(target_dir=debug_dir)
    run_asset_clone(debug=debug, asset_name=asset_name)
