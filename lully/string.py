
import datetime
from typing import Optional, Union

def surrounded(d: str, *, by='"') -> str:
    return (by if not d.startswith(by) else '') + d + (by if not d.endswith(by) else '')

def isfloat(s: str) -> bool:
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False

def isisodatetime(s: str) -> Optional[datetime.datetime]:
    try:
        return datetime.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None

def hide(s: str, ratio: Union[int, float] = 0.95, *, char: str = '•') -> str:
    """Hide given string content with char in place,

    for `ratio` percent of the string (if 0.<=ratio<=1.) :

    >>> hide('aaabbccc', ratio=0.5)
    'aa••••cc'

    or only showing `ratio` characters (if ratio >= 0) :

    >>> hide('aaabbccc', ratio=5)
    'aaa•••cc'

    >>> hide('aaaabbaaaa', 0.99, char='×')
    '××××××××××'
    >>> hide('aaaabbaaaa', 0.2, char='.')
    'aaaa..aaaa'
    >>> hide('aabbaaaa', 0.)
    'aabbaaaa'
    >>> hide('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', char='.')
    'aaa...............................................................................................aa'
    >>> hide('', ratio=0.)
    ''
    >>> hide('', ratio=1.)
    ''
    >>> hide('aaabbccc', ratio=1000)
    'aaabbccc'
    >>> hide('aaabbccc', ratio=3)
    'aa•••••c'
    >>> hide('aaabbccc', ratio=1)
    'a•••••••'
    >>> hide('aaabbccc', ratio=0)
    '••••••••'

    """
    if isinstance(ratio, float) and 0<=ratio<=1.:
        nb_to_hide = round(ratio * len(s))
    elif isinstance(ratio, int) and ratio >= 0:
        nb_to_hide = len(s) - min(ratio, len(s))
    else:
        raise TypeError(f"Ratio {ratio} is not a ratio (0.<=r<=1.) nor a positive integer")

    nb_to_show = len(s) - nb_to_hide
    assert nb_to_show >= 0, nb_to_show
    nb_to_show_per_side = nb_to_show // 2
    nb_to_show_supp = nb_to_show % 2
    # print(len(s), nb_to_show_per_side, nb_to_show_supp, nb_to_hide)
    return s[:nb_to_show_per_side + nb_to_show_supp] + char * nb_to_hide + (s[-nb_to_show_per_side:] if nb_to_show_per_side else '')
