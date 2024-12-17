import argparse
import os

from asset_manager.commands.asset_actions.download import DownloadAsset
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run_download(config: AssetDebug, files: list = None):
    args = argparse.Namespace()
    args.files = files
    config.run(callable=lambda: DownloadAsset().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    asset_name = "run/1"
    cfg = AssetDebug(asset_location=os.path.join(debug_dir, asset_name))
    run_download(config=cfg)
