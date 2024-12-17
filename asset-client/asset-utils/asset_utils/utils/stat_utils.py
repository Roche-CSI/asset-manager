import os

FIELDS = ["st_mode",
          "st_ino",
          "st_dev",
          "st_nlink",
          "st_uid",
          "st_gid",
          "st_size",
          "st_atime",
          "st_mtime",
          "st_ctime"]


def stat2dict(stat: os.stat_result):
    """returns dict from stat object"""
    return {key: getattr(stat, key) for key in FIELDS}
