
import random


def lsample(nb:int, it:iter, it_size=None, *, random=random.random) -> set:
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


def weighed_choice(choices: dict = None, **choices_as_dict):
    if choices is None and not choices_as_dict:
        raise ValueError(f"No valid parameter given.")
    if choices is None:
        choices = dict(choices_as_dict)

    is_int = all(isinstance(v, int) for v in choices.values())
    is_float = all(isinstance(v, float) for v in choices.values())

    if is_int:
        total = sum(choices.values())
        choice_index = random.randint(1, total)
        for choice, weight in choices.items():
            choice_index -= weight
            if choice_index <= 0:
                return choice
        raise RuntimeError(f"this shouldn't happen")

    elif is_float:
        total = round(sum(choices.values()))
        if total != 1:
            raise ValueError(f"Given weights are floats, but does not add up to 1 (instead, to {total} ({round(sum(choices.values()), 2)}))")
        choice_index = random.random()
        for choice, weight in choices.items():
            choice_index -= weight
            if choice_index <= 0:
                return choice
        raise RuntimeError(f"this shouldn't happen")

    else:
        raise ValueError(f"Input choices weights must be all int, or all float")


