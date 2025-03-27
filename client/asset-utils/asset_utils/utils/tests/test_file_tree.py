from asset_utils.utils.file_tree import TreeNode


def test_parse():
    paths = [
        "root/child1",
        "root/child2"
    ]
    root = TreeNode.parse(paths)
    assert "root" in root.children
    assert "child1" in root.children["root"].children
    assert "child2" in root.children["root"].children


def test_print_tree(capsys):
    root = TreeNode("root")
    child1 = TreeNode("child1")
    child2 = TreeNode("child2")
    root.add_child(child1)
    root.add_child(child2)
    TreeNode.print_tree(root)
    captured = capsys.readouterr()
    expected_output = "│root\n│└──child1\n│└──child2\n"
    assert captured.out == expected_output
