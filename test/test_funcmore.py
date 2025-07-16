
from lully.funcmore import iden, t_iden


def test_iden():
    assert 1 + iden(2) == 3
    assert iden(iden) is iden

def test_iden_t():
    a = {}
    assert a is t_iden(dict)(a)
