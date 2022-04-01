
from lully import itermore

TESTS = {
    'window': {
        ('ABC', 2): (('A', 'B'), ('B', 'C')),
        ('ABCD', 2): (('A', 'B'), ('B', 'C'), ('C', 'D')),
        ('ABC', 3): (('A', 'B', 'C'),),
        ('ABCD', 3): (('A', 'B', 'C'), ('B', 'C', 'D')),
    },
    'grouper': {
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


def create_test_window(func: callable, args, expected):
    def test_func():
        res = tuple(func(*args))
        assert res == expected
    return test_func

for tested_func, tests in TESTS.items():
    for idx, (val, out) in enumerate(tests.items(), start=1):
        globals()[f'test_{tested_func}_{idx}'] = create_test_window(getattr(itermore, tested_func), val, out)


