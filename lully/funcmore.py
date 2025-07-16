"""Supplementary functions for functools"""

import inspect
from typing import Callable, TypeVar


def x(*funcs, reverse=False):
    """return h=f×g×…

    >>> x(list, sorted)((2, 1))
    [1, 2]
    >>> x(str, tuple, sorted)((2, 1))
    '(1, 2)'
    >>> x(str, tuple, sorted, reverse=True)((2, 1))
    [' ', '(', ')', ',', '1', '2']

    """
    def __x(*args, **kwargs):
        first, *rests = funcs if reverse else reversed(funcs)
        v = first(*args, **kwargs)
        for f in rests:
            v = f(v)
        return v
    return __x


def has_param(f: Callable, p: str) -> bool:
    """True if given function f accepts p as a parameter

    >>> has_param(lambda x: x, 'x')
    True
    >>> has_param(lambda x: x, 'y')
    False
    >>> def f(a, /, b, *, c): return
    >>> has_param(f, 'a')
    True
    >>> has_param(f, 'b')
    True
    >>> has_param(f, 'c')
    True
    >>> has_param(f, 'd')
    False
    >>> has_param(2, 'd')
    False

    """
    try:
        args = inspect.getfullargspec(f)
    except Exception:
        return False
    return any(p in e for e in args if e)


T = TypeVar('T')
def iden(v: T) -> T:
    """Identity function

    >>> 1 + iden(2)
    3
    >>> iden(iden) is iden
    True

    """
    return v


K = TypeVar('K')
def t_iden(K) -> Callable[[K], K]:
    """Typing friendly identity function, allowing you to type explicitely"""
    def iden(v: K) -> K:
        return v
    return iden

