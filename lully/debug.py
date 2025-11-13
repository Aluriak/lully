import os
import marshal
import requests
import functools
from typing_extensions import TypeAlias

def get_cached(url: str, local_fname: str = 'todel.answer.data', kind: str = '', **kwargs) -> requests.Request:
    kind = kind or ('json' if url.endswith('.json') else 'text')
    if os.path.exists(local_fname):
        with open(local_fname, 'rb') as fd:
            data = marshal.load(fd)
    else:
        ans = requests.get(url)
        data = ans.json() if kind == 'json' else ans.text
        with open(local_fname, 'wb') as fd:
            marshal.dump(data, fd)
    return data


def shobj(obj, discard='_', maxwidth=100, indent='\t', print=print):
    print(indent, f"obj {obj} of type {type(obj)}:", sep='')
    for attr in dir(obj):
        if not attr.startswith(discard):
            v = repr(getattr(obj, attr))
            if isinstance(v, (bytes, str)) and len(v) > maxwidth:
                v = v[:30] + '[…]' + v[-30:]
            print(indent+indent, attr, v)


def printf(func = lambda *a, **k: None):
    """Add debug context to given function, if any is provided"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(func.__name__ + ':', *args, ' '.join(f"{kwarg}={repr(val)}" for kwarg, val in kwargs.items()), end='')
        r = func(*args, **kwargs)
        print(' \t-->', r, '' if r is None else type(r))
        return r
    return wrapper

def dryed(func, returns = None):
    """Add debug context, but do not run the function"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(func.__name__ + ':', *args, ' '.join(f"{kwarg}={repr(val)}" for kwarg, val in kwargs.items()), end='')
        pass  # no func call
        print(' \t-->', returns, '[DRY RUN]')
        return returns
    return wrapper

T: TypeAlias = object
def id(obj: T) -> T:
    "identity function ; do nothing to the object ; it just returns it"
    return obj
