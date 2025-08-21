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
        return a + b

    with pytest.raises(TypeError) as err:
        funcA(**EFFECTIVE_PARAMETERS)

    # with fief, the problem is gone
    assert fief(funcA)(**EFFECTIVE_PARAMETERS) == 5


def test_positionals_orders():
    @fief
    def func(a, b, /, c):
        return a + b * c

    with pytest.raises(TypeError) as err:
        assert func(2, 2, b=1) == 4

    assert func(2, 2, 1) == 4
    assert func(3, b=1, c=2) == 5  # b is passed to func as positional argument, despite being set here as a kwarg


def test_fief_with_positionals():
    params = {
        'b': 3,
        'c': 4,
    }

    def funcA(a, b):
        return a + b

    with pytest.raises(TypeError) as err:
        funcA(2, **params)

    # with fief, the problem is gone
    assert fief(funcA)(2, **params) == 5


def test_base_api():
    def func(a: int, /, b, *, c=1):
        return a + b + c

    assert fief.call(func, a=1, b=2, c=4, d=8) == 7
    assert fief(func)(a=1, b=2, d=8) == 4
    with pytest.raises(TypeError):  # missing params
        fief.call(func, b=2)


def test_decorator_api():
    @fief
    def func(a: int, /, b, *, c=1):
        return a + b + c

    assert func(a=1, b=2, c=4, d=8) == 7
    assert func(a=1, b=2, d=8) == 4
    with pytest.raises(TypeError):  # missing params
        func(b=2)
