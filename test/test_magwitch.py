from lully import magwitch


def test_basic_api():
    @magwitch.on
    def func(ok:bool):
        return ok
    assert func(True) is True
    assert func(False) is False
    assert func.ok() is True
    assert func.not_ok() is False


def test_modified_accessor():
    @magwitch.on_with(enable='with_', disable='never_')
    def func(ok:bool=False):
        return ok
    assert not hasattr(func, 'ok')
    assert not hasattr(func, 'not_ok')
    assert hasattr(func, 'with_ok')
    assert hasattr(func, 'never_ok')
    assert func.with_ok() is True
    assert func.never_ok() is False


def test_recursive():
    @magwitch.on
    def func(a:bool, b:bool=False):
        return a, b
    func.not_a  # ensure that there is no side effect when accessed
    assert func(True) == (True, False)
    assert func(False, False) == (False, False)
    assert func.a() == (True, False)
    assert func.b.a() == (True, True)
    # you can even repeat them !
    assert func.a.no_a.not_b.b() == (False, True)
    assert func.not_a.b.a.no_b() == (True, False)


def test_stock_default():
    @magwitch.on_with(use_defaults=True)
    def func(ko:bool=False):
        return ko
    assert func() is False
    assert func.ko() is False
    assert func.not_ko() is True


def test_with_default_as_true():
    @magwitch.on_with(use_defaults=True)
    def func(ok:bool=True):
        return ok
    assert func() is True
    assert func(True) is True
    assert func(False) is False
    assert func.ok() is True
    assert func.no_ok() is False  # both are available by default
    assert func.not_ok() is False


def test_with_default_as_false():
    @magwitch.on_with(use_defaults=False)  # this is default behavior
    def save_fig(in_png:bool=False):
        return in_png
    assert save_fig() is False
    assert save_fig(True) is True
    assert save_fig(False) is False
    assert save_fig.in_png() is True
    assert save_fig.not_in_png() is False
