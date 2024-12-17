from asset_manager.commands.asset_actions import get_actions as asset_actions
from asset_manager.commands.cmd_group import CommandGroup
from asset_manager.commands.parser import CommandParser


def test_asset_actions():
    parser = CommandParser()
    parser.add_actions(*asset_actions())
    args, unknwon = parser.parse_args(["add", "myfile.txt"])
    assert args.group == "add"


def test_parse_groups():
    parser = CommandParser()
    class_group = CommandGroup(name="class",
                               help="commands that applies to asset-class",
                               description="commands that applies to asset-class",
                               actions=asset_actions()
                               )

    parser.add_action_groups(class_group)
    args, unknown = parser.parse_args(["class", "add", "myfile.txt"])
    assert args.group == "class" and args.action == "add"
    assert args.target == ["myfile.txt"]


def test_actions_and_groups_together():
    parser = CommandParser()
    parser.add_actions(*asset_actions())
    class_group = CommandGroup(name="class",
                               help="commands that applies to asset-class",
                               description="commands that applies to asset-class",
                               actions=asset_actions()
                               )
    parser.add_action_groups(class_group)
    args, unknown = parser.parse_args(["add", "myfile.txt"])
    assert args.group == "add"

    args, unknwon = parser.parse_args(["class", "add", "myfile.txt"])
    assert args.group == class_group.name
    assert args.action == "add"
    assert args.target == ["myfile.txt"]
