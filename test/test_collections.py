
from lully.collections import Otom


def test_otom_basic_api():
    O = Otom({
        'one': 1,
        'two': 2,
        'tee': 3,
    })
    O[0] = 'zero'

    assert O['zero'] == 0
    assert O[1] == 'one'
    assert O[2] == 'two'
    assert O[3] == 'tee'
    assert 'one' == O[1]
    assert 'two' == O[2]
    assert 'tee' == O[3]
    assert O[0] == 'zero'

    O[3] = 'three'
    assert O[3] == 'three'
    assert 'three' == O[3]

    del O[3]
    assert 3 not in O
    assert 'three' not in O
    assert 'tee' not in O

    assert set(O) == {'one', 'two', 0}
    assert len(O) == 3
    assert set(O.keys()) == {'one', 'two', 0}
    assert set(O.values()) == {1, 2, 'zero'}
    assert set(O.allkeys()) == {'one', 'two', 'zero', 1, 2, 0}


def test_otom_comparisons():

    A = Otom({
        'one': 1,
        'two': 2,
        'tee': 3,
    })
    B = Otom(one=1, two=2, tee=3)
    C = Otom({  # note the inversion of keys and vals, which shouldn't really change anything
        1: 'one',
        2: 'two',
        3: 'tee',
    })

    assert {'one': 1, 1: 'one', 'two': 2, 2: 'two', 'tee': 3, 3: 'tee'} == {1: 'one', 'one': 1, 2: 'two', 'two': 2, 3: 'tee', 'tee': 3}
    assert A == B
    assert A == C
    assert B == C

    for O in (A, B, C):
        for key, val in O.items():
            assert O[key] == val
            assert O[val] == key


def test_otom_dict_methods():

    O = Otom({
        'one': 1,
        'two': 2,
        'tee': 3,
    })

    O.update({'foo': 4})
    assert O['foo'] == 4
    assert O[4] == 'foo'

    O.update({'tee': 6})
    assert O['tee'] == 6
    assert O[6] == 'tee'
    assert 3 not in O
