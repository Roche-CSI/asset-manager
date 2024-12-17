import argparse
import os

from asset_manager.commands.asset_actions.status import AssetStatus
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run_asset_status(config: AssetDebug):
    args = argparse.Namespace()
    config.run(callable=lambda: AssetStatus().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    asset_name = "v2_objects/2"
    cfg = AssetDebug(asset_location=os.path.join(debug_dir, asset_name))
    run_asset_status(config=cfg)
