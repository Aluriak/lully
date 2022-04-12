
from lully import lsample, weighed_choice


def test_lsample():
    assert lsample(3, [1, 2, 3]) == {1, 2, 3}
    assert lsample(1, [1, 2, 3]) < {1, 2, 3}
    assert len(lsample(2, [1, 2, 3]) & {1, 2, 3}) == 2


def test_weighed_choice():
    for _ in range(100):
        found = ''.join(weighed_choice(a=3, b=1) for _ in range(100))
        assert found.count('a') > found.count('b'), found  # this assert may fail with a likelihood of sum((1/4)**n for n in range(50, 101)), i.e. 1e-30
        # since it is ran one hundred times, it should fail once every 1e28 tests call.
        # good enough.
