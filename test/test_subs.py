
from lully.subs import multi_replace, rreplace


def test_multirep():
    assert multi_replace('aa a a', {'a': 'b'}) == 'aa b b'

def test_multirep_is_not_applying_sequenced_subs():
    assert multi_replace('b ab', {'a': 'b', 'b': 'cc'}) == 'cc ab'

def test_rreplace():
    assert rreplace('aaaabaaabba', 'b', 'c', 2) == 'aaaabaaacca'
    assert rreplace('aaaabaaabba', 'b', 'c') == 'aaaabaaabca'
    assert rreplace('aaaabaaabba', 'b', 'c', -1) == 'aaaacaaacca'
