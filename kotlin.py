"""Functions inspired from Kotlin lang"""
import itertools


def first(collection:[Object], condition=lambda _: True, default=None) -> Object:
    """
    >>> first("abc")
    "a"
    >>> first("abc", lambda x: x!="a")
    "b"
    >>> first("abc", lambda x: x=="z", default="w")
    "w"
    """
    for elem in collection:
        if condition(elem):
            return elem
    return default


def last(collection:[Object], condition=lambda _: True, default=None) -> Object:
    """
    >>> last("abc")
    "c"
    >>> last("abc", lambda x: x!="c")
    "b"
    >>> last("abc", lambda x: x=="z", default="w")
    "w"
    """
    return first(reversed(collection), condition, default)


def zip_with_next(collection:iter, nb_next:int=2, default_value=None):
    """
    >>> tuple(zip_with_next("abc"))
    (("a", "b"), ("c", None))
    """
    args = [iter(collection)] * n
    yield from itertools.zip_longest(*args, fillvalue=fillvalue)

# alias for the same function
window = zip_with_next
