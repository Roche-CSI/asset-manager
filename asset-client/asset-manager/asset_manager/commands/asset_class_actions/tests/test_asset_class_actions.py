from asset_manager.commands.asset_class_actions import get_action_group
from asset_manager.commands.parser import CommandParser


def test_parsing():
    parser = CommandParser()
    parser.add_action_groups(get_action_group())
    args, unknown = parser.parse_args(["class", "list"])
    assert args.group == "class" and args.action == "list"
