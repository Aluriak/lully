"""Functions inspired from Kotlin lang"""


import itertools


def first(collection:[object], condition=lambda _: True, default=None) -> object:
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


def last(collection:[object], condition=lambda _: True, default=None) -> object:
    """
    >>> last('abc')
    'c'
    >>> last('abc', lambda x: x!='c')
    'b'
    >>> last('abc', lambda x: x=='z', default='w')
    'w'
    """
    return first(reversed(collection), condition, default)


def zip_with_next(collection:iter, nb_next:int=2, fillvalue=None):
    """Like zip_longest, but with itself.

    >>> tuple(zip_with_next('abc'))
    (('a', 'b'), ('c', None))

    """
    args = [iter(collection)] * nb_next
    yield from itertools.zip_longest(*args, fillvalue=fillvalue)

#alias to the same function with a more popular name
window = zip_with_next
