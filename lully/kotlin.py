"""Functions inspired from Kotlin lang"""


import lully
import itertools
from typing import Iterable, TypeVar

T = TypeVar('T')

def first(collection: Iterable[T], condition=lambda _: True, default=None) -> T:
    """
    >>> first('abc')
    'a'
    >>> first('abc', lambda x: x!='a')
    'b'
    >>> first('abc', lambda x: x=='z', default='w')
    'w'
    """
    for elem in collection:
        if condition(elem):
            return elem
    return default


def last(collection: Iterable[T], condition=lambda _: True, default=None) -> T:
    """
    >>> last('abc')
    'c'
    >>> last('abc', lambda x: x!='c')
    'b'
    >>> last('abc', lambda x: x=='z', default='w')
    'w'
    """
    return first(reversed(tuple(collection)), condition, default)


zip_with_next = lully.window
# def zip_with_next(collection: Iterable[T], nb_next:int=2, fillvalue=None) -> Iterable[tuple[T]]:
    # """Like zip_longest, but with itself.

    # Note that is is strictly equivalent to window function

    # >>> tuple(zip_with_next('abc'))
    # (('a', 'b'), ('c', None))

    # """
    # args = [iter(collection)] * nb_next
    # yield from itertools.zip_longest(*args, fillvalue=fillvalue)
