
from random import random


def lsample(nb:int, it:iter, it_size=None, *, random=random) -> set:
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
        nb_elem = len(it)
    else:
        nb_elem = it_size
    assert nb <= nb_elem
    # implementation
    for elem in it[:nb_elem]:
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
