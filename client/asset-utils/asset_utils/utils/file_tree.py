from __future__ import annotations

import os.path

PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "


class TreeNode(object):
    value: str = None
    children: dict = None

    def __init__(self, path: str = None):
        self.path = path
        self.children = {}
        if path:
            comps = str(path).split(sep=os.sep)
            self.value = comps.pop(0)
            if comps:
                self.add_child(TreeNode(path=os.path.join(*comps)))

    def add_child(self, node: TreeNode):
        if node.value not in self.children:
            self.children[node.value] = node
        else:
            for child in node.children.values():
                self.children[node.value].add_child(child)

    @classmethod
    def print_tree(cls, root, marker_str=ELBOW, level_markers=[]):
        empty_str = " " * len(marker_str) * 2
        connection_str = PIPE + empty_str[:-1]
        level = len(level_markers)
        mapper = lambda draw: connection_str if not draw else empty_str
        markers = "".join(map(mapper, level_markers[:-1]))
        markers += marker_str if level > 0 else ""
        if root.value:
            print(f"{PIPE}{markers}{root.value}")

        children = list(root.children.values())
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            cls.print_tree(child, marker_str, [*level_markers, not is_last])

    @classmethod
    def parse(cls, paths: [str]):
        node = TreeNode()
        for path in paths:
            node.add_child(TreeNode(path))
        return node
