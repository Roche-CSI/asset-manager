import fnmatch


def filter_blobs(blobs: list, name_key: str, pattern: str = None, ignore: [str] = None):
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
