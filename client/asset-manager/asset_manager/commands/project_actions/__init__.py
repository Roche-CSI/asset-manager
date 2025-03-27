from .project_info import ProjectInfo
from .project_activate import ProjectActivate
from .project_list import ProjectList
from asset_manager.commands.cmd_group import CommandGroup


def get_actions():
    return [
        ProjectInfo(),
        ProjectActivate(),
        ProjectList()
    ]


def get_action_group():
    group = CommandGroup(name="project",
                         help="asset-manager project commands",
                         description="asset-manager project commands",
                         actions=get_actions(),
                         default_action=ProjectInfo()
                         )
    group.requires_store = False
    group.requires_repo = False
    group.requires_auth = False
    return group
