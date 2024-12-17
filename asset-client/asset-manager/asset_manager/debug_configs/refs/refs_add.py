import argparse
import os

from asset_manager.commands.refs_actions.ref_add import AddRef
from asset_manager.debug_configs.refs.refs_debug import RefsDebug


def run(config: RefsDebug, files: list = None):
    args = argparse.Namespace()
    args.src = "dsa_assets/1/0.0.0"
    args.dst = "dsa_assets/2/0.0.0"
    args.label = "ref-check"
    args.remote = False
    args.properties = None
    config.run(callable=lambda: AddRef().run(args=args))


if __name__ == "__main__":
    debug_dir = "/Users/mahantis/am_demo/dsa_assets/1"
    asset_name = ""
    cfg = RefsDebug(asset_location=os.path.join(debug_dir, asset_name))
    run(config=cfg)
