from packaging.version import parse, Version

MAX_VERSION_NUMBER = 99
START_VERSION = "0.0.0"


def increment_version(existing):
    """increments version and returns the new version"""
    # todo: migrate this to server
    if not existing:
        return START_VERSION
    curr_ver = parse(existing)
    # read only properties, so we need some holding vars
    major, minor, micro = curr_ver.major, curr_ver.minor, curr_ver.micro
    # increment version
    micro = micro + 1 if (micro < MAX_VERSION_NUMBER - 1) else 0
    if micro == 0:
        minor += 1
    if minor > MAX_VERSION_NUMBER:
        minor = 0
    if minor == 0 and micro == 0:
        major += 1  # no max version constraints on major
    # get a new version object so that we can compare and make sure it incremented
    new_ver = Version(f"{major}.{minor}.{micro}")
    # make sure it confirms to versioning scheme i.e. greater than previous version
    assert new_ver > curr_ver
    return str(new_ver)


def version_to_int(version_str):
    """Converts a version string to an integer using a weighted sum approach"""
    try:
        ver = parse(version_str)
        return ver.major * 1000000 + ver.minor * 1000 + ver.micro
    except ValueError:
        raise ValueError(f"Invalid version string: {version_str}")
