import os
import argparse
from asset_manager.debug_configs.asset.asset_debug import AssetDebug
from asset_manager.commands.asset_actions.union import AssetUnion


def run_version_union_dry_run(debug: AssetDebug, target_ver: str):
    args = argparse.Namespace()
    args.dst_version = target_ver
    args.file = None
    args.continue_file = None
    debug.run(callable=lambda: AssetUnion().run(args=args))


def run_version_union_continue(debug: AssetDebug, file: str):
    args = argparse.Namespace()
    args.dst_version = None
    args.file = None
    args.continue_file = file
    debug.run(callable=lambda: AssetUnion().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/Development/asset_manager/repos/asset_client/asset-manager/debug_data"
    asset_name = "acap-test-data/1"
    # asset_name = "dsaswe_test/23"
    debug = AssetDebug(debug_dir=debug_dir, asset_name=asset_name)
    # file = "/var/folders/s0/zjyp4c395_j7_4_l5f80z3fr0000gn/T/tmpptyfudh4/eyJhc3Nl.txt"
    file = "/var/folders/s0/zjyp4c395_j7_4_l5f80z3fr0000gn/T/tmpmd0ej5ys/eyJhc3Nl.txt"
    # run_version_union_dry_run(debug=debug, target_ver="0.0.30")
    run_version_union_continue(debug=debug, file=file)
