
import os
import __main__

def is_repl() -> bool:
    return not hasattr(__main__, '__file__')


def envvar_is_true(envvar: str, *, default: bool = False) -> bool:
    v = os.environ.get(envvar, default)
    if isinstance(v, str) and v.isnumeric():
        return bool(int(v))
    if isinstance(v, str) and v.lower() in {'no', 'n', 'non', 'nop', 'nope', 'none', 'false'}:
        return False
    return bool(v)

def envvar_is_false(envvar: str, *, default: bool = False) -> bool:
    return not envvar_is_true(envvar, default=default)
