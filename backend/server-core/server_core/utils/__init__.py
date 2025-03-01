from typing import Iterable, Union, List, Dict, Callable
import collections.abc
import datetime
from pytz import utc, timezone
from time import time
import functools
import contextlib
import pwd
import os

PROFILE, PRINT_ARGS = True, False


@contextlib.contextmanager
def time_it(desc: str):
    ts = time()
    yield
    te = time()
    print(f'func: {desc} took: {te - ts:.2f} sec')


def time_it_wrapper(f):
    @functools.wraps(f)
    def wrap(*args, **kw):
        if PROFILE:
            ts = time()
            result = f(*args, **kw)
            te = time()
            if PRINT_ARGS:
                print(f'func:{f.__name__} args:[{args}, {kw}] took: {te-ts:.2f} sec')
            else:
                print(f'func:{f.__name__} took: {te - ts:.2f} sec')
        else:
            result = f(*args, **kw)
        return result
    return wrap


def cast2list(item: Union[Iterable[str], str, None]) -> List[str]:
    """takes single object or a collection and casts to List"""
    if item is None:
        return []
    if isinstance(item, str):
        return [item]
    return list(item)


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

# can't use timezone name here because datetime.strptime doesn't support it on
# linux (works on Mac though)
# '%Y-%m-%dT%H-%M-%S %Z' doesn't work on Linux with python3.7 and 3.8
DATE_FORMAT = '%Y/%m/%d %H-%M-%S %z'
TIME_ZONE = 'US/Pacific'


def time_now():
    return datetime.datetime.now(tz=utc).replace(microsecond=0)


def convert_to_pst(ts: datetime):
    return ts.astimezone(timezone(TIME_ZONE)).strftime(DATE_FORMAT)

def get_user_id():
    """Returns the user_id of the system"""
    return pwd.getpwuid(os.getuid()).pw_name

def string_to_timestamp(date_string):
    t = datetime.datetime.strptime(date_string, DATE_FORMAT)
    return t.timestamp()