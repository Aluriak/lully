
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


def user_inputs_yes(text: str, default: str = 'yes', true_if: str = 'yes', suffix: str = '[{y}/{n}] ') -> bool:
    YESY_VALUES = 'y', 'yes', 'yeah', 'o', 'oui', '1', True
    NOSY_VALUES = 'n', 'no', 'non', 'nop', 'nope', '0', False
    answer = input(text + suffix.format(
        y='Y' if default in YESY_VALUES else 'y',
        n='N' if default in NOSY_VALUES else 'n',
    )).strip().lower()
    if not answer or answer not in YESY_VALUES+NOSY_VALUES:
        answer = default
    if true_if in YESY_VALUES:
        return answer in YESY_VALUES
    else:
        return answer in NOSY_VALUES
