from asset_manager.commands.cmd_group import CommandGroup

from .store_clear import StoreClear
from .store_info import StoreInfo
from .store_prune import StorePrune
from .store_set import StoreSet


def get_actions():
    return [
        StoreInfo(),
        StoreClear(),
        StoreSet(),
        StorePrune()
    ]


def get_action_group():
    group = CommandGroup(name="store",
                         help="asset store commands",
                         description="asset store functionalities",
                         actions=get_actions(),
                         default_action=StoreInfo()
                         )
    group.requires_repo = False
    group.requires_store = False
    return group
