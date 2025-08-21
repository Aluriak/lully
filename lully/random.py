
import math
import random
from itertools import islice
from typing import Callable, Iterable, Optional, Sized


def lsample(nb: int, it: Iterable, it_size: Optional[int] = None, *, random: Callable = random.random) -> set:
    """Return a subset of given iterable of given size.

    Implementation of Vitter's algorithm for the n choose k problem.

    it_size must be the size of given iterable, if len() can't be called on it.

    The algorithm behave as follow.
    It is performed in a O(|it|). For each element, the probability to found it
    in the output subset is equal to:
        (number of element in the subset) / (number of elements in it)

    for the n-th element, the probability is equivalent to:
        (number of element not already in the subset) /
        (number of non-treated elements in it)


    """
    # parameters treatment
    choosens = set()  # set of the nb_choosen elements of it
    if it_size is None:
        assert isinstance(it, Sized), it
        nb_elem = len(it)
    else:
        nb_elem = it_size
    assert nb <= nb_elem
    # implementation
    for elem in islice(it, 0, nb_elem):
        likelihood = nb / nb_elem  # modified later, depending of elem
                                             # inclusion in the choosens set
        assert 0 <= likelihood <= 1.
        if random() <= likelihood:
            choosens.add(elem)
            nb -= 1
        nb_elem -= 1
        if nb == 0:  # no more element to choose
            break
    return choosens


def randsum(total: int, outsize: int, maxsub: Optional[int] = None) -> list[int]:
    """Yield a list of numbers whose sum is the given total.

    None for maximum list size means any number is allowed.

    >>> sum(randsum(50, 5))
    50
    >>> len(randsum(50, 5))
    5
    >>> randsum(5, 1, maxsub=5)[0]
    5

    """
    if maxsub is None:
        maxsub = total + 1  # maximal list size is 1+1+1+1+1+1+…
    assert outsize <= total
    assert maxsub * outsize >= total
    found = []
    remaining_size = outsize
    remaining_total = total
    # decide the first outsize-1 random subs
    while len(found) < outsize - 1:
        new_value = random.randint(1, min(remaining_total - (remaining_size), maxsub))
        found.append(new_value)
        remaining_total -= new_value
        remaining_size -= 1
    # ensure the last one doesn't exceed maxsub ; if so, redistribute among non maximal ones
    if remaining_total > maxsub:
        for _ in range(remaining_total - maxsub):
            incrementables = [i for i in range(len(found)) if found[i] < maxsub]
            assert incrementables, incrementables
            idx = random.choice(incrementables)
            found[idx] += 1
    # add the last sub
    found.append(min(remaining_total, maxsub))
    assert sum(found) == total, (found, sum(found), total)
    assert all(f <= maxsub for f in found), (found, maxsub)
    return found

