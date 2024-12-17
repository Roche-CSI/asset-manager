import argparse
import os

from asset_manager.commands.asset_actions.switch import AssetSwitch
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run_switch(config: AssetDebug, version):
    args = argparse.Namespace()
    args.version = True
    args.number = version
    config.run(callable=lambda: AssetSwitch().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    asset_name = "acap-test-data/1"
    cfg = AssetDebug(asset_location=os.path.join(debug_dir, asset_name))
    run_switch(config=cfg, version="0.0.30")
