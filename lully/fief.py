"""
This module implements a decorator that allows a complete filtering of
effective parameters with respect to the formal ones.

"""

from inspect import signature
from functools import wraps


def filter_effective_parameters(func):
    """Decorator that filter out parameters in kwargs that are not related to
    any formal parameter of the given function.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        formal_parameters = frozenset(signature(func).parameters.keys())
        return func(*args, **{
            arg: value
            for arg, value in kwargs.items()
            if arg in formal_parameters
        })
    return wrapper
