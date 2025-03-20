from asset_manager.commands.cmd_group import CommandGroup
from .info import PackageInfo


def get_actions():
    return [
        PackageInfo()
    ]


def get_action_group():
    group = CommandGroup(name="package",
                         help="asset-manager package information",
                         description="asset-manager package information",
                         actions=get_actions(),
                         default_action=PackageInfo()
                         )
    group.requires_store = False
    group.requires_repo = False
    group.requires_auth = False
    return group
