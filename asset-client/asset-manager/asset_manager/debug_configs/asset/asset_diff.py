import os
import argparse
from asset_manager.commands.asset_actions.diff import AssetDiff
from asset_manager.debug_configs.asset.asset_debug import AssetDebug


def run_version_diff(debug: AssetDebug):
    args = argparse.Namespace()
    args.src_ver = "0.0.39"
    args.dst_ver = "0.0.40"
    debug.run(callable=lambda: AssetDiff().run(args=args))


def run_file_diff(debug: AssetDebug):
    args = argparse.Namespace()
    args.src_ver = "0.0.30"
    args.dst_ver = "0.0.40"
    args.file = "ac_analysis/lib/online/tests/expected_offline_controller_data/negative_pore_annotations.json"
    args.html = True
    debug.run(callable=lambda: AssetDiff().run(args=args))


if __name__ == "__main__":
    data_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    asset_name = "acap-test-data/1"
    debug = AssetDebug(asset_location=os.path.join(data_dir, asset_name))
    # run_version_diff(config=config)
    run_file_diff(debug=debug)
