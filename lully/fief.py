"""Implementation of Fief"""

import inspect
from typing import Callable, Generic, TypeVar
from functools import wraps


T = TypeVar('T')

class fief(Generic[T]):

    def __init__(self, func: Callable[..., T]):
        """Decorator that filter out parameters in kwargs that are not related to
        any formal parameter of the given function.

        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            spec = inspect.getfullargspec(func)
            pos_args = [kwargs[arg] for arg in spec.args[len(args):] if arg in kwargs]
            kwo_args = {arg: kwargs[arg] for arg in spec.kwonlyargs if arg in kwargs}
            return func(*args, *pos_args, **kwo_args)
        self._func = func
        self._wrapped = wrapped

    def __call__(self, *args, **kwargs) -> T:
        return self._wrapped(*args, **kwargs)

    @staticmethod
    def call(f: Callable[..., T], *args, **kwargs) -> T:
        return fief(f)(*args, **kwargs)



def old_call(f: Callable[..., T], **kwargs) -> T:
    spec = inspect.getfullargspec(f)
    pos_args = [kwargs[arg] for arg in spec.args if arg in kwargs]
    kwo_args = {arg: kwargs[arg] for arg in spec.kwonlyargs if arg in kwargs}
    return f(*pos_args, **kwo_args)
