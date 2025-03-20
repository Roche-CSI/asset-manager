from asset_manager.commands.cmd_group import CommandGroup
from .ref_add import AddRef
from .ref_info import RefsInfo
from .ref_remove import RemoveRef


def get_actions():
    return [
        AddRef(),
        RefsInfo(),
        RemoveRef()
    ]


def get_action_group():
    group = CommandGroup(name="inputs",
                         help="asset-manager inputs commands",
                         description="asset-manager inputs commands",
                         actions=get_actions())
    group.requires_store = True
    group.requires_repo = False
    return group
