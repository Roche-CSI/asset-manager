from asset_manager.commands.parser import CommandParser
from asset_manager.commands.asset_actions.add import AddToAsset


def test_asset_actions():
    parser = CommandParser()
    parser.add_actions(
        AddToAsset()
    )

    args, unknown = parser.parse_args(["add", "myfile.txt", "--proxy"])
    assert args.group == "add" and args.target == ["myfile.txt"]
    assert args.proxy
    assert not args.dest_dir

    args, unknown = parser.parse_args(["add", "myfile.txt", "--proxy", "--dir", "new_dir"])
    assert args.group == "add" and args.target == ["myfile.txt"]
    assert args.proxy
    assert args.dest_dir and args.dest_dir == "new_dir"

    args, unknown = parser.parse_args(["add", "gs://model_visualizations/zhul76/dl-training-zhul76-2022-06-09T17-05-45-PDT/*.png", "--proxy", "--dir", "new_dir"])
    assert args.group == "add" and args.target == ["gs://model_visualizations/zhul76/dl-training-zhul76-2022-06-09T17-05-45-PDT/*.png"]
    assert args.proxy
    assert args.dest_dir and args.dest_dir == "new_dir"
