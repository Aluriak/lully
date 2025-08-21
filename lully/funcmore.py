"""Supplementary functions for functools"""

import inspect
import lully as ll
from typing import Callable, TypeVar
from collections import namedtuple


def x(*funcs: Callable, reverse: bool = False, fief: bool = True) -> Callable:
    """Return h=f×g×…

    x(f,g)(v) == f×g(v) == g(f(v))

    Expect each function to take the output of previous function as first output.
    To get a splat operator between functions, see y.


    >>> def f(a, b): return a, b
    >>> def g(c, d): return c, d
    >>> x(f, g)(1, 2, b=3)
    ((1, 2), 3)


    >>> x(list, sorted)((2, 1))
    [1, 2]
    >>> x(str, tuple, sorted)((2, 1))
    '(1, 2)'
    >>> x(str, tuple, sorted, reverse=True)((2, 1))
    [' ', '(', ')', ',', '1', '2']

    """
    def __x(*args, **kwargs):
        first, *rests = funcs if reverse else reversed(funcs)
        v = (ll.fief(first) if fief else first)(*args, **kwargs)
        for f in rests:
            v = (ll.fief(f) if fief else f)(v, **kwargs)
        return v
    return __x


def y(*funcs: Callable, reverse: bool = False, fief: bool = True) -> Callable:
    """Return h=f×g×…

    Splat version of x, where y(f,g)(v) == g(*f(v))

    >>> def f(a, b): return a, b
    >>> def g(c, d): return c, d
    >>> y(f, g)(1, 2)
    (1, 2)
    >>> y(f, g)(1, d=2)
    (1, 2)

    """
    def __y(*args, **kwargs):
        first, *rests = funcs if reverse else reversed(funcs)
        v = (ll.fief(first) if fief else first)(*args, **kwargs)
        for f in rests:
            f = (ll.fief(f) if fief else f)
            if isinstance(v, (list, tuple)) and len(v) > 1:  # splat operator looks expected
                v = f(*v, **kwargs)
            else:
                v = f(v, **kwargs)
        return v
    return __y


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

