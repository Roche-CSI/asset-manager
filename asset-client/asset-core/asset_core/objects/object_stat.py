from __future__ import annotations

from asset_contents.file_stat import FileStat


class ObjectStat(FileStat):
    linked = False

    @classmethod
    def serialize_fields(cls):
        return [
            "id",  # file id
            "content_time",  # last content modification time
            "metadata_time",  # number of hardlinks
            "num_links",  # time of last metadata change
            "inode",  # inode number
            "size",  # file size
            "linked"
        ]
