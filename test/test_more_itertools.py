

from lully import window


TESTS = {
    ('ABC', 2): (('A', 'B'), ('B', 'C')),
    ('ABCD', 2): (('A', 'B'), ('B', 'C'), ('C', 'D')),
    ('ABC', 3): (('A', 'B', 'C'),),
    ('ABCD', 3): (('A', 'B', 'C'), ('B', 'C', 'D')),
}


def create_test_window(args, expected):
    def test_func():
        res = tuple(window(*args))
        assert res == expected
    return test_func

for idx, (val, out) in enumerate(TESTS.items(), start=1):
    globals()[f'test_window_{idx}'] = create_test_window(val, out)

