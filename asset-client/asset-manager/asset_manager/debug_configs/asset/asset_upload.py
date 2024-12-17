import argparse
import os

from asset_core.configs.configs import Configs, ConfigModes
from asset_manager.commands.asset_actions.upload import UploadAsset
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run_upload(config: AssetDebug):
    args = argparse.Namespace()
    args.message = "sample"
    Configs.shared(mode=ConfigModes.DEV)
    config.run(callable=lambda: UploadAsset().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data/dsaswe_test/23"
    asset_name = ""
    cfg = AssetDebug(asset_location=os.path.join(debug_dir, asset_name))
    run_upload(config=cfg)
