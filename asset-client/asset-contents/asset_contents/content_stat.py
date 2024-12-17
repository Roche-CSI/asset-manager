from __future__ import annotations

from .file_stat import FileStat


class ContentStat(FileStat):
    refs: list = []  # number of object references
    hash: str = None

    def __init__(self, id=None, src=None):
        super(ContentStat, self).__init__(id, src)
        self.refs = []

    def add_ref(self, ref):
        if ref not in self.refs:
            self.refs.append(ref)

    def remove_ref(self, ref):
        if ref in self.refs:
            self.refs.remove(ref)

    def serialize(self):
        data = {key: getattr(self, key) for key in self.__class__.serialize_fields()}
        return data

    @classmethod
    def de_serialize(cls, data: dict) -> ContentStat:
        data = data or {}
        ref = ContentStat()
        for key in cls.serialize_fields():
            setattr(ref, key, data.get(key))
        if ref.refs is None:
            ref.refs = []
        return ref

    @classmethod
    def serialize_fields(cls):
        return [
            "id",  # file id
            "content_time",  # last content modification time
            "metadata_time",  # number of hardlinks
            "num_links",  # time of last metadata change
            "inode",  # inode number
            "size",  # file size
            "refs",
            "hash"
        ]

    def __repr__(self):
        return self.id
