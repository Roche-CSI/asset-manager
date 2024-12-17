import contextlib


class File(object):
    path: str = None
    cloned: bool = None
    linked_path = None
    size: int = None  # file size in bytes

    def __init__(self, path, linked_path, cloned, size):
        self.path = path
        self.linked_path = linked_path
        self.cloned = cloned
        self.size = size

    def __str__(self):
        return self.linked_path

    @contextlib.contextmanager
    def open(self, mode: str = "r"):
        yield open(self.linked_path, mode=mode)
