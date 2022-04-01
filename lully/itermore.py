"""Even more itertools !

Some functions are joyfully collectivized from itertools documentation.

"""

import operator
import collections
from itertools import chain, zip_longest, islice, repeat


def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return chain.from_iterable(repeat(tuple(iterable), n))


def dotproduct(vec1, vec2):
    return sum(map(operator.mul, vec1, vec2))


def convolve(signal, kernel):
    # See:  https://betterexplained.com/articles/intuitive-convolution/
    # convolve(data, [0.25, 0.25, 0.25, 0.25]) --> Moving average (blur)
    # convolve(data, [1, -1]) --> 1st finite difference (1st derivative)
    # convolve(data, [1, -2, 1]) --> 2nd finite difference (2nd derivative)
    kernel = tuple(kernel)[::-1]
    n = len(kernel)
    window = collections.deque([0], maxlen=n) * n
    for x in chain(signal, repeat(0, n-1)):
        window.append(x)
        yield sum(map(operator.mul, kernel, window))


def flatten(list_of_lists: list) -> iter:
    "Flatten one level of nesting"
    return chain.from_iterable(list_of_lists)


def grouper(iterable, n, fillvalue=None) -> iter:
    """Collect data into fixed-length chunks or blocks

    >>> tuple(map(''.join, grouper('ABCDEFG', 3, 'x')))
    ('ABC', 'DEF', 'Gxx')
    >>> tuple(grouper('ABC', 2))
    (('A', 'B'), ('C', None))

    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def window(it:iter, size:int=2) -> iter:
    it = iter(it)
    window = collections.deque(islice(it, 0, size), maxlen=size)
    while True:
        yield tuple(window)
        try:
            window.append(next(it))
        except StopIteration:
            return
