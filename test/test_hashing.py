"""tests of the hashing methods"""
from lully.hashing import human_code, NOUNS, ADJECTIVES


def test_human_code():
    assert isinstance(human_code('1'), str)
    for i in range(1000):
        print(i, human_code(str(i)))
        assert human_code(str(i)) == human_code(str(i))
        assert ' ' in human_code(str(i))
    # assert False


def test_doublons_in_hcode():
    ko = False
    from collections import Counter
    for kind in (NOUNS, ADJECTIVES):
        c = Counter(kind)
        for n, nb in c.items():
            if nb > 1:
                print(n, nb)
                ko = True
    if ko:
        print("Doublons dans les mots")
        assert False
