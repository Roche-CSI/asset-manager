import collections.abc
import contextlib
import datetime
import fnmatch
import functools
import os
import pwd
import re
from contextlib import contextmanager
from functools import wraps
from itertools import islice
from os.path import expanduser
from time import time
from typing import Iterable, Union, List, Dict, Callable

from pytz import utc, timezone

from asset_utils.common import DEBUG, PROFILE, PRINT_ARGS
from asset_utils.utils.log_utils import UserLog

# can't use timezone name here because datetime.strptime doesn't support it on
# linux (works on Mac though)
# '%Y-%m-%dT%H-%M-%S %Z' doesn't work on Linux with python3.7 and 3.8
DATE_FORMAT = '%Y/%m/%d %H-%M-%S %z'
TIME_ZONE = 'US/Pacific'


def contains_special_chars(string: str) -> bool:
    """Checks if the string contains any restricted special chars.

    Allowed special chars are: '_', '.', and '-'

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    bool
        True if the string contains only allowed special chars, False otherwise.
    """
    return bool(re.search(r'[^a-zA-Z0-9_.-]', string))


def is_integer(n):
    try:
        float(n)
    except Exception:
        return False
    else:
        return float(n).is_integer()


def batch(iterable, batch_size: int = 1):
    iterable_size = len(iterable)
    batch_size = max(batch_size, 1)
    for ndx in range(0, iterable_size, batch_size):
        yield iterable[ndx: min(ndx + batch_size, iterable_size)]


def time_now():
    return datetime.datetime.now(tz=utc).replace(microsecond=0)


def convert_to_pst(ts: datetime):
    return ts.astimezone(timezone(TIME_ZONE)).strftime(DATE_FORMAT)


def date_to_string(dt: datetime.datetime):
    return dt.strftime(DATE_FORMAT)


def string_to_timestamp(date_string):
    try:
        t = datetime.datetime.strptime(date_string, DATE_FORMAT)
    except ValueError as e:
        print(f"error converting date string:{e}")
        UserLog().error(f"{e}")
        t = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H-%M-%S-%Z')
    return t.timestamp()


def chunks(data, SIZE=10000):
    """splits dictionary into chunks"""
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in islice(it, SIZE)}


def get_user_id():
    """Returns the user_id of the system"""
    return pwd.getpwuid(os.getuid()).pw_name


def get_time_stamp():
    """Returns current time with time zone"""
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def make_dirs(file_path: str):
    """creates intermediate directories for the filepath"""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)


def user_home_dir():
    return expanduser("~")


def update_dict(d, u) -> dict:
    """
    recursively updates d with u
    :param d: dict to update
    :param u: dict with new values
    :return: updated dict
    """
    d = d or {}
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, type(v)()), v)
        else:
            d[k] = v
    return d


def env2bool(var, undefined=False) -> bool:
    """
    undefined: return value if env var is unset
    """
    var = os.getenv(var, None)
    if var is None:
        return undefined
    return bool(re.search("1|y|yes|true", var, flags=re.I))


def cast2list(item: Union[Iterable[str], str, None]) -> List[str]:
    """takes single object or a collection and casts to List"""
    if item is None:
        return []
    if isinstance(item, str):
        return [item]
    return list(item)


def relative_path(path, start=os.curdir) -> str:
    """returns relative path of file"""
    path = os.fspath(path)
    start = os.path.abspath(os.fspath(start))
    return os.path.relpath(path, start)


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string[:]


def remove_suffix(string: str, suffix: str) -> str:
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    else:
        return string[:]


def files_at_location(src, ignore=None):
    src = os.path.abspath(src)
    if os.path.isdir(src):
        return list_files(src, ignore=ignore)
    elif os.path.isfile(src):
        return cast2list(src)
    else:
        # user may have passed a wild card character like *.txt or data?.txt
        # check for wildcards
        if "*" in src or "?" in src or "[" in src:
            dir_name = os.path.dirname(src) or os.getcwd()
            pattern = src[len(dir_name) + 1:]
            return list_files(root_dir=dir_name, pattern=pattern, ignore=ignore)
    return []


def find_pattern(string: str):
    pattern = None
    if "*" in string or "?" in string or "[" in string:
        wildcard_idx = lowest_positive([string.find('*'), string.find('?'), string.find("[")])
        if wildcard_idx > -1:
            pattern = string[wildcard_idx:]
    return pattern


def lowest_positive(numbers: []):
    lowest = -1
    for number in numbers:
        if number < 0:
            continue
        if lowest == -1 or number < lowest:
            lowest = number
    return lowest


def first_matching_dir(root_dir: str, pattern: str):
    """Returns the first matching directory in the given root_dir recursively.

    Parameters
    ----------
    root_dir : str
        The root directory to search in.
    pattern: str
        The pattern to match the directory name.
    """
    for dir_path, dir_names, _ in os.walk(root_dir):
        for dir_name in dir_names:
            if fnmatch.fnmatch(dir_name, pattern):
                return os.path.join(dir_path, dir_name)
    return None


def list_files(root_dir,
               pattern: str = None,
               ignore: str = None,
               recurse: bool = True) -> list:
    """lists all files (absolute paths) recursively in the directory
    Parameters:
        root_dir:   str
                    directory in which to list the files
        pattern:    str
                    optional, if passed lists files matching pattern
        ignore:     bool
                    optional, if passed, files matching pattern are ignored
        recurse:    bool
                    optional, default is to search recursively
    """
    if recurse:
        return __list_recursive(root_dir=root_dir, pattern=pattern, ignore=ignore)
    else:
        return __list_non_recursive(root_dir=root_dir, pattern=pattern, ignore=ignore)


def __list_recursive(root_dir,
                     pattern: str = None,
                     ignore: str = None) -> list:
    """
    Searches directory recursively and lists all files
    imp: not using glob here because of potential hidden directories
    Parameters
    ----------
    root_dir
    pattern
    ignore

    Returns
    -------

    """
    parsed = []
    pattern = os.path.join(root_dir, pattern) if pattern else None
    ignores = ignore.split(",") if ignore else []
    ignores = [os.path.join(root_dir, ignore) if ignore else None for ignore in ignores]
    # ignore = os.path.join(root_dir, ignore) if ignore else None
    for root, dirs, files in os.walk(root_dir):
        file_paths = [os.path.join(root, file) for file in files]
        file_names = fnmatch.filter(file_paths, pattern) if pattern else file_paths
        # ignore_names = fnmatch.filter(file_paths, ignore) if ignore else []
        ignore_names = get_ignore_names(ignores, file_paths)
        for file in file_names:
            if file in ignore_names:
                continue
            parsed.append(file)
    return parsed


def get_ignore_names(ignores, paths):
    result = set()
    for ignore in ignores:
        files = fnmatch.filter(paths, ignore) if ignore else []
        for file in files:
            result.add(file)
    return list(result)


def __list_non_recursive(root_dir,
                         pattern: str = None,
                         ignore: str = None) -> list:
    parsed = []
    files = os.listdir(root_dir)
    file_names = fnmatch.filter(files, pattern) if pattern else files
    ignore_names = fnmatch.filter(files, ignore) if ignore else []
    for file in file_names:
        if file in ignore_names:
            continue
        parsed.append(os.path.join(root_dir, file))

    return parsed


def rsetattr(obj, attr, val):
    """recursively sets values in nested attributes
    source: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
    """
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    """recursively gets values from nested attributes
    source: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
    """

    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))


def args_choices(choices: Dict[int or str, Iterable]) -> Callable:
    """decorator factory: force arguments of a func limited inside the given choices

    :param choices: a dict which describes the choices of arguments
        the key of the dict must be either the index of options or the key(str) of kwargs
        the value of the dict must be an iterable."""
    err_fmt = "value of '{}' is not a valid choice in {}"

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            for arg_index in range(len(args)):
                param_name = func.__code__.co_varnames[arg_index]
                if arg_index in choices and args[arg_index] not in choices[arg_index]:
                    raise ValueError(err_fmt.format(param_name, choices[arg_index]))
                elif param_name in choices and args[arg_index] not in choices[param_name]:
                    raise ValueError(err_fmt.format(param_name, choices[param_name]))
            for param_name in kwargs:
                if param_name in choices and kwargs[param_name] not in choices[param_name]:
                    raise ValueError(err_fmt.format(param_name, choices[param_name]))

            return func(*args, **kwargs)

        return decorated_func

    return decorator


def time_elapsed(message, ts, te):
    print(f'{message} took: {te - ts:.2f} sec')


@contextlib.contextmanager
def time_it(desc: str):
    ts = time()
    yield
    te = time()
    print(f'func: {desc} took: {te - ts:.2f} sec')


def time_it_wrapper(f):
    @wraps(f)
    def wrap(*args, **kw):
        if DEBUG and PROFILE:
            ts = time()
            result = f(*args, **kw)
            te = time()
            if PRINT_ARGS:
                print(f'func:{f.__name__} args:[{args}, {kw}] took: {te - ts:.2f} sec')
            else:
                print(f'func:{f.__name__} took: {te - ts:.2f} sec')
        else:
            result = f(*args, **kw)
        return result

    return wrap


@contextmanager
def ch_dir(path):
    cur_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cur_dir)
