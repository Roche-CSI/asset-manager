import os

from asset_core.api.store_api import CloneAssetAPI
from asset_manager.commands import CliAction, CliOption
from asset_utils.common.user_commands import UserCommands


class CloneAsset(CliAction):
    name = "clone"
    help_msg = "clone an asset to local or remote location"
    requires_repo = False

    def run(self, args):
        if not args.asset_name:
            self.user_log.alert("missing required parameter asset-name")
            self.user_log.message(UserCommands().clone_asset())
            return

        target_dir = os.path.abspath(args.dir) if args.dir else None
        api = CloneAssetAPI()
        if args.credentials:
            os.environ["ASSET_CREDENTIALS"] = args.credentials
        # user used remote flag but did not provide the remote url
        if args.remote is None:
            self.user_log.alert("missing the remote-url to clone the asset")
            return
        # user used version flag but did not provide the version number
        if args.version is None:
            self.user_log.alert("missing the version number of the asset")
            return
        with api.environment():
            if args.remote:
                # compare storage prefix to prevent cross platform remote clone
                if not os.path.commonprefix([args.remote, api.store.storage_url()]):
                    self.user_log.alert("can not clone to a different storage platform")
                    return
                api.remote_clone(asset_name=args.asset_name, remote_url=args.remote)
                return
            # clone asset to local directory
            api.clone_asset(asset_name=args.asset_name,
                            target_dir=target_dir,
                            recursive=args.r,
                            force=args.force,
                            soft=args.soft,
                            version=args.version)
            # unset credentials
            if args.credentials:
                os.unsetenv("ASSET_CREDENTIALS")

    def get_options(self):
        return [
            CliOption(
                dest="asset_name",
                help_msg="name of the asset. can be <class-name>/<seq_id> "
                         "or <class-name>/<alias>. can also use <asset-name>/<file-name> "
                         "or <asset-name>/<name-pattern> to clone parts of the asset",
                positional=True
            ),
            CliOption(
                dest="r",
                help_msg="recursive, if True, all referenced assets will also be cloned",
                is_boolean=True
            ),
            CliOption(
                dest="dir",
                help_msg="optional: a directory name where asset would be cloned",
                short_name="d",
                full_name="dir"
            ),
            CliOption(
                dest="force",
                help_msg="to override any existing files/directory in the target asset location",
                short_name="f",
                is_boolean=True
            ),
            CliOption(
                dest="soft",
                help_msg="optional: shallow clone i.e. only asset meta information, but not the actual files",
                short_name="s",
                is_boolean=True
            ),
            CliOption(
                dest="credentials",
                help_msg="optional: gcs/aws credentials to use for cloning (for proxy assets)",
                short_name="c",
                full_name="cred"
            ),
            CliOption(
                dest="remote",
                help_msg="optional: a remote directory where asset would be cloned",
                short_name="re",
                full_name="remote"
            ),
            CliOption(
                dest="version",
                help_msg="optional: version of the asset to clone, defaults to latest version if missing",
                short_name="v",
                full_name="version"
            ),
        ]
