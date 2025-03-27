import os

from asset_core.api.store_api import CopyAPI
from asset_manager.commands import CliAction, CliOption


class CopyObject(CliAction):
    name = "cp"
    help_msg = "copy files and objects from source to destination"
    requires_repo = False
    requires_store = False

    def run(self, args):
        if not args.src or not args.dst:
            self.user_log.error("missing required parameters src and dst")
            return
        api = CopyAPI()
        if args.credentials:
            os.environ["ASSET_CREDENTIALS"] = args.credentials
        with api.environment():
            api.copy(src=args.src,
                     dst=args.dst,
                     recursive=args.recursive,
                     force=args.force,
                     skip_cmp=args.no_deduplicate)
            # unset credentials
            if args.credentials:
                os.unsetenv("ASSET_CREDENTIALS")

    def get_options(self):
        return [
            CliOption(dest="src",
                      help_msg="source of the object to copy",
                      positional=True),
            CliOption(dest="dst",
                      help_msg="destination where objects would be copied to",
                      positional=True),
            CliOption(dest="credentials",
                      help_msg="optional: gcs/aws credentials to use for copying",
                      short_name="c",
                      full_name="cred"),
            CliOption(dest="recursive",
                      short_name="r",
                      full_name="recursive",
                      help_msg="recursive, use this flag to copy directories",
                      is_boolean=True),
            CliOption(dest="force",
                      short_name="f",
                      full_name="force",
                      help_msg="overwrite any existing files/directory without asking for confirmation",
                      is_boolean=True),
            CliOption(dest="no_deduplicate",
                      short_name="n",
                      full_name="no_deduplicate",
                      help_msg="disable filtering out files that are already present in the destination\n."
                               "as files are compared by their hash, use this flag to "
                               "skip the hash computation and make the copy faster",
                      is_boolean=True),
        ]
