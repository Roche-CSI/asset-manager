import argparse
import os

from asset_manager.commands.asset_actions.info import AssetInfo
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run(config: AssetDebug):
    args = argparse.Namespace()
    config.run(callable=lambda: AssetInfo().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    asset_name = "dsaswe_test/23"
    cfg = AssetDebug(asset_location=os.path.join(debug_dir, asset_name))
    run(config=cfg)
