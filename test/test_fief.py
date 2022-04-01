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
