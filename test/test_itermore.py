

import lully as ll

def test_groupby():
    objs = [{'n': 'a', 'g': 1}, {'n': 'b', 'g': 1}, {'n': 'c', 'g': 2}]
    expected = {
        1: [{'n': 'a', 'g': 1}, {'n': 'b', 'g': 1}],
        2: [{'n': 'c', 'g': 2}]
    }
    assert ll.groupby(objs, 'g') == expected

    f = lambda d: d['n']
    assert ll.groupby(objs, 'g', apply=f) == {1: ['a', 'b'], 2: ['c']}


def test_groupby_with_getter():
    import operator
    objs = [('Lucas', 'CDC'), ('Basile', 'DIM'), ('Sacha', 'CDC'), ('Bertrand', 'CDC'), ('Guillaume', 'DIM')]
    found = ll.groupby(objs, key=1, apply=lambda p: p[0])
    assert isinstance(found, dict)
    assert set(found.keys()) == {'CDC', 'DIM'}
    assert set(found['CDC']) == {'Lucas', 'Sacha', 'Bertrand'}


def test_divide():
    f = ll.divide

    gen = (1, 2, 3, 4)
    pred = lambda x: bool(x % 2)

    odd, even = map(list, f(gen, pred))
    assert even == [2, 4]
    assert odd == [1, 3]


TESTS: dict[str, dict[tuple, tuple]] = {
    'window': {
        ('ABC', 2): (('A', 'B'), ('B', 'C')),
        ('ABCD', 2): (('A', 'B'), ('B', 'C'), ('C', 'D')),
        ('ABC', 3): (('A', 'B', 'C'),),
        ('ABCD', 3): (('A', 'B', 'C'), ('B', 'C', 'D')),
    },
    'chunks': {
        ('ABCDEFG', 3, 'x'): (('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')),
    },
    'ncycles': {
        ('ABC', 2): ('A', 'B', 'C', 'A', 'B', 'C'),
        ('A', 6): ('A', 'A', 'A', 'A', 'A', 'A'),
    },
    'flatten': {
        (((1, 2), (3, 4)),): (1, 2, 3, 4),
    },
}


def create_test_window(func, args, expected):
    def test_func():
        res = tuple(func(*args))
        assert res == expected
    return test_func

for tested_func, tests in TESTS.items():
    for idx, (val, out) in enumerate(tests.items(), start=1):
        globals()[f'test_{tested_func}_{idx}'] = create_test_window(getattr(ll.itermore, tested_func), val, out)

