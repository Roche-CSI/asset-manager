from __future__ import annotations

import os


class FileStat(object):
    # file id
    id = None
    # file data modification time
    content_time: float = None
    # content modification time
    metadata_time: float = None
    # number of hardlinks
    num_links: int = None
    # file size
    size: int = None
    # inode
    inode: int = None

    def __init__(self, id=None, src=None):
        self.id = id
        if src:
            self.translate(stat=os.stat(src))

    def translate(self, stat: os.stat_result):
        mappings = self.__class__.mapped_fields()
        for field in mappings:
            setattr(self, mappings.get(field), getattr(stat, field))

    def serialize(self):
        data = {key: getattr(self, key) for key in self.__class__.serialize_fields()}
        return data

    @classmethod
    def de_serialize(cls, data: dict) -> FileStat:
        data = data or {}
        stat = FileStat()
        for key in cls.serialize_fields():
            setattr(stat, key, data.get(key))
        return stat

    @classmethod
    def serialize_fields(cls):
        return [
            "id",  # file id
            "content_time",  # last content modification time
            "metadata_time",  # number of hardlinks
            "num_links",  # time of last metadata change
            "inode",  # inode number
            "size",  # file size
        ]

    @classmethod
    def mapped_fields(cls):
        """ Note:
        st_ctime      Time when file status was last changed (inode data modification). Changed by the chmod(2),
                      chown(2), link(2), mknod(2), rename(2), unlink(2), utimes(2) and write(2)
                      system calls.

        st_mtime      Time when file data last modified.  Changed by the
                      mknod(2), utimes(2) and write(2) system calls.

        Write operations change both st_mtime (content_time) and st_ctime(metadata time)
        Rename, link or delete (unlink) will change only st_ctime (metadata_time)
        move -> doesn't affect st_mtime but affects st_ctime

        Python documentation is bad, below has better description
        https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/stat.2.html
        """
        return {
            "st_ctime": "metadata_time",  # time of last metadata change
            "st_mtime": "content_time",  # last content modification time
            "st_nlink": "num_links",  # number of hardlinks
            "st_ino": "inode",  # inode number
            "st_size": "size",  # file size
        }

    def __repr__(self):
        return self.id
