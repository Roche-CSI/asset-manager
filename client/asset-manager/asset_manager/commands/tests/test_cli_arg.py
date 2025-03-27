from asset_manager.commands.cli_option import CliOption


def test_create():
    arg = CliOption(dest="target",
                    help_msg="target files/dirs/urls to add to the asset",
                    positional=True)
    assert arg.dest == "target"
