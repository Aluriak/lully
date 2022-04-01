
from lully import lsample


def test_lsample():
    assert lsample(3, [1, 2, 3]) == {1, 2, 3}
    assert lsample(1, [1, 2, 3]) < {1, 2, 3}
    assert len(lsample(2, [1, 2, 3]) & {1, 2, 3}) == 2
