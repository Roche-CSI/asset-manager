import argparse
import os

from asset_manager.commands.asset_actions.add import AddToAsset
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run(config: AssetDebug, files: list = None):
    args = argparse.Namespace()
    args.target = ["*"]
    args.credentials = None
    args.yes = True
    args.proxy = False
    args.dest_dir = None
    args.ignore = None
    args.type = "group"
    config.run(callable=lambda: AddToAsset().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data/dsaswe_test/23"
    asset_name = ""
    cfg = AssetDebug(asset_location=os.path.join(debug_dir, asset_name))
    run(config=cfg)
