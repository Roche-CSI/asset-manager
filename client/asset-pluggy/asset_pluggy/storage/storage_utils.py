import copy
import fnmatch
import os

from asset_utils.utils.file_utils import FileUtils
from asset_utils.utils.in_memory_zip import InMemoryZip


def filter_blobs(blobs: list,
                 name_key: str,
                 pattern: str = None,
                 ignore: [str] = None) -> list:
    """Filter the blobs based on the pattern and ignore.

    TODO: Use unix style pattern matching for filtering the blobs.
    """
    if ignore:
        # ignore_patterns = ignore.split(",")
        not_ignored = []
        for blob in blobs:
            if not _is_ignored(getattr(blob, name_key), ignore):
                not_ignored.append(blob)
    else:
        not_ignored = list(blobs)

    if pattern:
        result = [blob for blob in not_ignored if _is_matched(getattr(blob, name_key), pattern)]
    else:
        result = not_ignored
    return result


def _is_matched(path, pattern=None):
    if not pattern:
        return True
    return fnmatch.fnmatch(path, pattern)


def _is_ignored(path: str, ignores: [str] = None):
    if not ignores:
        return False
    for ignore in ignores:
        if fnmatch.fnmatch(path, ignore):
            return True
    return False


# used in asset-server
def parse_for_saving_to_bucket(data: list):
    parsed = copy.deepcopy(data)
    for item in parsed:
        item["data"] = serialize_for_file(filename=item["url"], filedata=item["data"])
    return parsed


# used in asset-server
def serialize_for_file(filename: str, filedata):
    _, ext = os.path.splitext(filename)
    if ext in [".yaml", ".yml"]:
        return FileUtils.yaml_serialize(filedata)
    elif ext in [".json"]:
        return FileUtils.json_serialize(filedata)
    elif ext in [".zip"]:
        memzip = InMemoryZip()
        serialized = []
        for filename in filedata:
            # convert recursively
            serialized.append(serialize_for_file(filename, filedata[filename]))
        memzip.add_files(serialized)
        return memzip
    else:
        return filedata
