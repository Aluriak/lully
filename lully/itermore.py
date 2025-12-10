"""More itertools

Some functions are joyfully collectivized from itertools documentation.

"""
import itertools
import operator
from itertools import chain, islice, repeat, zip_longest
from collections import deque, defaultdict
from typing import Union, Iterable, Callable, TypeVar


__all__ = 'groupby', 'chunks', 'window', 'flatten', 'reversemap', 'divide', 'ncycles'


def groupby(iterable: Union[list, dict], key: object, *, getter: Callable = operator.getitem, apply: Callable = lambda x: x) -> dict[object, list]:
    r = defaultdict(list)
    for it in iterable:
        r[getter(it, key)].append(apply(it))
    return dict(r)


T = TypeVar('T')
F = TypeVar('F')
def chunks(iterable: Iterable[T], n: int, fillvalue: F = None) -> Iterable[Iterable[Union[T, F]]]:
    """Collect data into fixed-length chunks or blocks

    >>> tuple(map(''.join, chunks('ABCDEFG', 3, 'x')))
    ('ABC', 'DEF', 'Gxx')
    >>> tuple(chunks('ABC', 2))
    (('A', 'B'), ('C', None))

    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def chunks_nofill(iterable, n: int):
    """Collect data into fixed-length chunks, except for the last one,
    that will not be populated with a filler like in chunks()

    >>> tuple(chunks_nofill('ABC', 2))
    (('A', 'B'), ('C',))

    """
    args = [iter(iterable)] * n
    for payload in zip_longest(*args, fillvalue=None):
        yield tuple(p for p in payload if p is not None)

chunks.nofill = chunks_nofill  # type: ignore[attr-defined]



def window(it: Iterable, size: int=2):
    """Sliding window of given size on given iterable"""
    it = iter(it)
    window = deque(islice(it, 0, size), maxlen=size)
    while True:
        yield tuple(window)
        try:
            window.append(next(it))
        except StopIteration:
            return


def divide(it: Iterable, pred: Callable, buckets: Union[list, tuple] = (True, False)) -> Iterable[Iterable]:
    """Divide given iterable into len(buckets) iterable, each filled according
    to the output value of given callable

    """
    return (
        (w for w in subit if pred(w) == v)
        for v, subit in zip(buckets, itertools.tee(it, len(buckets)))
    )


def reversemap(d: dict, unique: bool = False, multival: bool = True, key2val: Callable = lambda x:x, val2key: Callable = lambda x: tuple(x) if isinstance(x, list) else (frozenset(x) if isinstance(x, set) else x)) -> dict:
    """Reverse given dictionnary. Map A>B becomes B>A, or B>list[A] if not unique.

    >>> reversemap({'a': 1, 'b': 2}, unique=True)
    {1: 'a', 2: 'b'}
    >>> reversemap({'a': 1, 'b': 1}, unique=True)
    {1: 'b'}
    >>> reversemap({'a': 1, 'b': 1})
    {1: ['a', 'b']}

    >>> reversemap({'a': [1, 2], 'b': 2}, unique=True)
    {1: 'a', 2: 'b'}
    >>> reversemap({'a': [1, 2], 'b': 2})
    {1: ['a'], 2: ['a', 'b']}
    >>> reversemap({'a': [1, 2], 'b': 2}, multival=False)
    {(1, 2): ['a'], 2: ['b']}

    """
    if unique:
        return {
            val2key(val): key2val(key)
            for key, vals in d.items()
            for val in (vals if multival and isinstance(vals, (list, tuple, set, frozenset)) else [vals])
        }
    ret = {}
    for key, vals in d.items():
        for val in (vals if multival and isinstance(vals, (list, tuple, set, frozenset)) else [vals]):
            ret.setdefault(val2key(val), []).append(key2val(key))
    return ret


def flatten(list_of_lists: list) -> Iterable:
    "Flatten one level of nesting"
    return chain.from_iterable(list_of_lists)


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
    window = deque([0], maxlen=n) * n
    for x in chain(signal, repeat(0, n-1)):
        window.append(x)
        yield sum(map(operator.mul, kernel, window))
