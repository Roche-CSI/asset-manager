from asset_manager.commands.cmd_group import CommandGroup
from .alias_add import AddAlias
from .alias_help import AliasHelp
from .alias_info import AliasInfo
from .alias_remove import RemoveAlias
from .alias_set import SetAlias


def get_actions():
    return [
        SetAlias(),
        AddAlias(),
        RemoveAlias(),
        AliasInfo(),
        AliasHelp()
    ]


def get_action_group():
    group = CommandGroup(name="alias",
                         help="asset-manager alias commands",
                         description="asset-manager alias commands",
                         actions=get_actions(),
                         default_action=AliasInfo()
                         )
    group.requires_store = True
    group.requires_repo = True
    group.requires_auth = True
    return group
