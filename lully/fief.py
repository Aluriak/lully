"""Implementation of Fief"""

import inspect
from typing import Callable, TypeVar
from functools import wraps


T = TypeVar('T')
def call(f: Callable[..., T], *args, **kwargs) -> T:
    return fief(f)(*args, **kwargs)


def fief(func: Callable) -> Callable:
    """Decorator that filter out parameters in kwargs that are not related to
    any formal parameter of the given function.

    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        formal_parameters = frozenset(inspect.signature(func).parameters.keys())
        return func(*args, **{
            arg: value
            for arg, value in kwargs.items()
            if arg in formal_parameters
        })
    return wrapped


fief.call = call



T = TypeVar('T')
def old_call(f: Callable[..., T], **kwargs) -> T:
    spec = inspect.getfullargspec(f)
    pos_args = [kwargs[arg] for arg in spec.args if arg in kwargs]
    kwo_args = {arg: kwargs[arg] for arg in spec.kwonlyargs if arg in kwargs}
    return f(*pos_args, **kwo_args)
