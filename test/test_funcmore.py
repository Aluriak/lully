
from lully.funcmore import iden, t_iden, x, y


def test_iden():
    assert 1 + iden(2) == 3
    assert iden(iden) is iden

def test_iden_t():
    a = {}
    assert a is t_iden(dict)(a)


def test_x_basic():
    def f(a): return a + 1
    def g(a): return a * 2
    assert x(f, g)(2) == 5
    assert x(g, f)(2) == 6
    assert x(f, g)(2, b=1) == 5  # fief enables us to avoid problems on superfluous parameter

def test_x_basic_types():
    assert x(str, tuple, sorted)((2, 1)) == '(1, 2)'


def test_x_with_fief_support():
    def f(a, b): return a + b
    def g(c, d): return c * d
    assert x(f, g)(1, d=2, b=3) == 5  # (1 * d) + b
    assert x(g, f)(1, d=2, b=3) == 8  # (1 + b) * d


def test_y_signatures():
    assert y(str, '|'.join)('hello') == 'h|e|l|l|o'
    assert y(print, '|'.join)('watever') is None
