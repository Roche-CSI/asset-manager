from asset_manager.commands.cmd_group import CommandGroup


def test_create():
    class_group = CommandGroup(name="class",
                               help="commands that applies to asset-class",
                               description="commands that applies to asset-class",
                               actions=[]
                               )
    assert class_group.name == "class"
