"""Various function helpers implementing operators on collections"""
import functools
from typing import Callable, Iterable, Any


def A2Bs_BA(a2bs: dict, *, fsum: Callable = lambda x,y: str(x) + str(y)) -> tuple:
    """
    >>> A2Bs_BA({'a': [1, 2], 'b': [3]})
    ('1a', '2a', '3b')
    """
    return tuple(
        fsum(val, key)
        for key, vals in a2bs.items()
        for val in vals
    )
def A2Bs_AB(a2bs: dict, *, fsum: Callable = lambda x,y: str(x) + str(y)) -> tuple:
    return tuple(
        fsum(key, val)
        for key, vals in a2bs.items()
        for val in vals
    )
def A2Bs_B2A(a2bs: dict) -> dict:
    return {
        val: key
        for key, vals in a2bs.items()
        for val in vals
    }

# class __transform:
    # def __call__(self, data: dict, tr: str) -> dict:
        # return f"do {tr} on {data}"
        # # for src, trg in ll.it.window(tr.split('_'), 2):
            # # if src.count('2') == 1:
                # # key, val = src.split('2')
    # def __getattr__(self, key):
        # if not key.startswith('_'):
            # return functools.partial(self, tr=key)
        # return super().__getitem__(key)
# transform = __transform()



def append_missings(ordered: list, to_append: Iterable, on_missing: Callable = tuple, outtype: type = tuple) -> list:
    """Return ordered + (to_append - ordered)

    >>> append_missings(range(1,7), {2, 4, 8})
    (1, 2, 3, 4, 5, 6, 8)
    >>> from lully import ẍ
    >>> ''.join(append_missings('ace', 'efb', on_missing=ẍ(sorted, list)))
    'acebf'
    >>> append_missings('ace', 'efb', on_missing=ẍ(sorted, list), outtype=list)
    ['a', 'c', 'e', 'b', 'f']

    """
    base = outtype(ordered)
    missings = on_missing(set(to_append) - set(base))
    return base + outtype(missings)


def merge_dicts(*ds: dict, fill: bool = False, fillvalue: Any = None) -> dict[Any, list[Any]]:
    """
    >>> merge_dicts({'a': 'b'}, {'a': 'c'})
    {'a': ['b', 'c']}
    >>> merge_dicts({'a': 'b'}, {'c': 'd'}, {'c': 'e'})
    {'a': ['b'], 'c': ['d', 'e']}
    >>> merge_dicts({'a': 'b', 'c': 'd'}, {'c': 'e'}, fill=True, fillvalue='X')
    {'a': ['b', 'X'], 'c': ['d', 'e']}
    >>> merge_dicts({'a': 'b'}, {'c': 'd'}, {'c': 'e'}, fill=True, fillvalue='X')
    {'a': ['b', 'X', 'X'], 'c': ['X', 'd', 'e']}
    >>> merge_dicts({'a': 'b', 'c': 'd'}, {'c': 'e'}, {'c': 'f'}, {'a': 'g', 'c': 'g'}, fill=True, fillvalue='X')
    {'a': ['b', 'X', 'X', 'g'], 'c': ['d', 'e', 'f', 'g']}
    """
    assert all(isinstance(d, dict) for d in ds), ds
    ret = {}
    for d in ds:
        newcols = [c for c in d if c not in ret]
        for col in list(ret):
            ret.setdefault(col, [])
            if fill or col in d:  # add either the d[val] or fillvalue
                ret[col].append(d.get(col, fillvalue))
        for col in newcols:
            ret[col] = [fillvalue] * (len(next(iter(ret.values()), []))-1) + [d[col]]
    return ret
