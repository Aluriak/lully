"""
Testing of the fief module.

"""

import pytest
from lully import fief


def test_fief_basic_api():
    EFFECTIVE_PARAMETERS = {
        'a': 2,
        'b': 3,
        'c': 4,
    }

    def funcA(a, b):
        return a, b

    with pytest.raises(TypeError) as err:
        funcA(**EFFECTIVE_PARAMETERS)

    # with fief, the problem is gone
    assert fief(funcA)(**EFFECTIVE_PARAMETERS) == (2, 3)

    # beware the multiple values, if you provide positionnal params
    with pytest.raises(TypeError) as err:
        assert fief(funcA)(0, **EFFECTIVE_PARAMETERS)
    assert fief(funcA)(0, **{'b': 3}) == (0, 3)


def test_positionals_orders():
    @fief
    def func(a, b, /, c):
        return a, b, c

    assert func(1, 2, 3) == (1, 2, 3)
    assert func(1, b=2, c=3) == (1, 2, 3)  # b is passed to func as positional argument, despite being set here as a kwarg

    with pytest.raises(TypeError) as err:
        func(1, 3, b=2)  # multiple values for parameter 'b' are given


def test_fief_with_positionals():
    params = {
        'b': 2,
        'c': 3,
    }

    def funcA(a, b):
        return a, b

    # we cannot send non existing parameters
    with pytest.raises(TypeError) as err:
        funcA(1, **params)

    # with fief, the problem is gone
    assert fief(funcA)(1, **params) == (1, 2)


def test_base_api():
    def func(a: int, /, b, *, c=10):
        return a, b, c

    assert fief.call(func, 1, b=2, c=3, d=4) == (1, 2, 3)
    assert fief(func)(a=1, b=2, d=8) == (1, 2, 10)
    with pytest.raises(TypeError):  # missing params
        fief.call(func, b=2)


def test_decorator_api():
    @fief
    def func(a: int, /, b, *, c=1):
        return a, b, c

    assert func(a=1, b=2, c=4, d=8) == (1, 2, 4)
    assert func(a=1, b=2, d=8) == (1, 2, 1)
    with pytest.raises(TypeError):  # missing params
        func(b=2)
