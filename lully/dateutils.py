"""Helpers around naive dates"""

import re
import ast
import locale
import datetime as datetime_mod
from datetime import datetime, date
import zoneinfo
from zoneinfo import ZoneInfo
from typing import Union, Optional, Any, Iterable


try:
    import dateutil
except ImportError:
    dateutil = None

REGEX_DATETIME_MATCH = r'([0-9T:T-]+)(\.[0-9]{0,6})[0-9]*([+-].*)'


def localized_strftime(dt: datetime, fmt: str, locale_code: tuple[str, str] = ('fr_FR', 'UTF-8')) -> str:
    "NOT THREAD-SAFE"
    old_loc = locale.getlocale()
    locale.setlocale(locale.LC_TIME, locale_code)
    ret = dt.strftime(fmt)
    locale.setlocale(locale.LC_TIME, old_loc)
    return ret

def localized_strptime(s: str, fmt: str, locale_code: tuple[str, str] = ('fr_FR', 'UTF-8')) -> datetime:
    "NOT THREAD-SAFE"
    old_loc = locale.getlocale()
    locale.setlocale(locale.LC_TIME, locale_code)
    ret = datetime.strptime(s, fmt)
    locale.setlocale(locale.LC_TIME, old_loc)
    return ret


def zone_info_from(obj: Union[str, ZoneInfo, datetime, Any], *, raises: Optional[Exception] = None) -> Optional[ZoneInfo]:
    "Tries hard to create a ZoneInfo object from input value"
    if isinstance(obj, ZoneInfo):
        return obj
    if isinstance(obj, str):
        return ZoneInfo(obj)
    if isinstance(obj, datetime):
        if str(obj.tzinfo) == 'UTC':
            return ZoneInfo('UTC')
        if isinstance(obj.tzinfo, ZoneInfo):
            return obj.tzinfo
        if isinstance(obj.tzinfo, datetime_mod.timezone):
            try:
                if obj.tzinfo:
                    return ZoneInfo(str(obj.tzinfo))
            except zoneinfo.ZoneInfoNotFoundError:
                if str(obj.tzinfo.utcoffset(obj)) == '1:00:00':
                    return ZoneInfo('Europe/Paris')
                else:
                    raise
        if tzname := obj.tzname():
            return ZoneInfo(tzname)
    if raises:
        raise raises
    return None


def time_since(d: Union[datetime, int, float], *, ref: Union[datetime, int, float] = None, precision: int = 2, joiner: str = ' et ') -> str:
    """Human repr of quantity of time separating given datetime and the given ref (or now if not provided)"""
    if isinstance(d, (float, int)):
        d = datetime.fromtimestamp(d)
    if isinstance(ref, (float, int)):
        _now = datetime.fromtimestamp(ref)
    elif isinstance(ref, datetime):
        _now = ref
    else:
        _now = now(zone=zone_info_from(d)) if dt_is_aware(d) else datetime.now()
    total = abs(round((_now - d).total_seconds()))
    return pretty_seconds(total, precision=precision, joiner=joiner)

def time_from_now(d: datetime, **kwargs) -> str:
    return time_since(d, ref=now() if dt_is_aware(d) else datetime.now(), **kwargs)


def pretty_seconds(s: int, *, precision: int = 0, repr_template: str = '{nb} {unit}', joiner: str = ', ', repr_now: str = "À l'instant", now_is_below: int = 1) -> str:
    """Show given number of seconds in a human-readable way"""
    DAY = 24*60*60
    LEAPS = {
        'siècle': 36500*DAY,
        'année': 365*DAY,
        'mois': 30*DAY,
        'semaine': 7*DAY,
        'jour': DAY,
        'heure': 60*60,
        'minute': 60,
        'seconde': 1
    }

    def most_significant_segments(ts, prec: int):
        if ts < now_is_below:
            yield None, None
            return
        for leap, in_seconds in LEAPS.items():
            nb_leap = round(ts // in_seconds)
            if nb_leap:
                yield nb_leap, leap
                prec -= 1
            if prec == 0:
                return
            ts %= in_seconds

    def with_s_if_many(name: str, nb: int) -> str:
        return name + ('s' if isinstance(nb, int) and nb > 1 and name[-1] != 's' else '')

    return joiner.join(
        repr_template.format(nb=ago_count, unit=with_s_if_many(ago_type, ago_count)) if ago_count else repr_now
        for ago_count, ago_type in most_significant_segments(s, prec=precision or len(LEAPS))
    )

def dt_is_naive(d: datetime) -> bool:
    return not dt_is_aware(d)
def dt_is_aware(d: datetime) -> bool:
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None

def delta_from_pretty(string: str) -> datetime_mod.timedelta:
    """

    >>> delta_from_pretty('1h').total_seconds()
    3600.0
    >>> delta_from_pretty('-1m').total_seconds()
    -60.0
    """
    AVAILABLE_UNITS = {'h': 'hours', 'H': 'hours', 'm': 'minutes', 'M': 'minutes', 'y': 'years', 'w': 'weeks', 'd': 'days', 's': 'seconds', 'S': 'seconds'}
    unit = string[-1]
    count = ast.literal_eval(string[:-1])
    if string[-1] not in AVAILABLE_UNITS:
        raise ValueError(f"Cannot handle unit {unit}: expects one of {','.join(AVAILABLE_UNITS)}")
    assert isinstance(count, (int, float)), string
    return datetime_mod.timedelta(**{AVAILABLE_UNITS[unit]: count})

def seconds_from_pretty(string: str) -> int:
    return round(delta_from_pretty(string).total_seconds())


def add_time(d: datetime, plus: Union[str, int, float], minus: Union[str, int, float] = 0) -> datetime:
    """add to given datetime a fixed amount of time, such as '7d', '-1w', '12s' or a number of seconds"""
    if isinstance(plus, (int, float)):
        plus = f'{plus}s'
    if isinstance(plus, str):
        delta_plus = delta_from_pretty(plus)
    else:
        raise ValueError(f"Cannot handle {plus} of type {type(plus)}")
    if isinstance(minus, (int, float)):
        minus = f'{minus}s'
    if isinstance(minus, str):
        delta_minus = delta_from_pretty(minus)
    else:
        raise ValueError(f"Cannot handle {minus} of type {type(minus)}")
    delta = delta_plus - delta_minus
    return d + delta

def add_days(d: datetime, nb: int) -> datetime:
    return add_time(d, f'{nb}d')

def nb_days(da: datetime, db: datetime) -> int:
    return abs((db - da).days)

def between_dates(start: datetime, end: datetime) -> Iterable[datetime]:
    "Yield each day between start and end, inclusive"
    assert start <= end
    assert isinstance(start, datetime), type(start)
    curr = start
    while curr <= end:
        yield curr
        curr = add_days(curr, 1)


def parse_isoformat_with_microseconds(dt: Union[int, str]) -> datetime:
    """Datetime only can parse milliseconds, hence that function

    >>> parse_isoformat_with_microseconds('2023-12-15T14:10:47.717263573+01:00')
    datetime.datetime(2023, 12, 15, 14, 10, 47, 717263, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))
    >>> parse_isoformat_with_microseconds('2023-12-15T14:10:47.0717263573+01:00')
    datetime.datetime(2023, 12, 15, 14, 10, 47, 71726, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))
    >>> datetime.fromisoformat('2025-04-02T11:10:04.835990+02:00')
    datetime.datetime(2025, 4, 2, 11, 10, 4, 835990, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))

    """
    if isinstance(dt, int):
        return datetime.fromtimestamp(dt)
    if isinstance(dt, str):
        if m := re.fullmatch(REGEX_DATETIME_MATCH, dt):
            a, b, c = m.groups()
            b = b.ljust(7, '0')
            return datetime.fromisoformat(a + b + c)
        if m := re.fullmatch('([0-9T:T-]+[+-].*)', dt):
            return datetime.fromisoformat(dt)
        raise ValueError(f"Given {dt} of type {type(dt)} is not an isoformat string of microsecond datetime")
    raise TypeError(f"Given {dt} of type {type(dt)} is not an isoformat string of microsecond datetime")

def first_time_of_day(dt: datetime, *, zone: Optional[Union[str, ZoneInfo]] = 'Europe/Paris') -> datetime:
    return datetime(year=dt.year, month=dt.month, day=dt.day, tzinfo=zone_info_from(dt))

def last_time_of_day(dt: datetime, *, zone: Optional[Union[str, ZoneInfo]] = 'Europe/Paris') -> datetime:
    return datetime(year=dt.year, month=dt.month, day=dt.day, tzinfo=zone_info_from(dt)) + datetime_mod.timedelta(hours=24, seconds=-1)

def now(*, zone: Optional[Union[str, ZoneInfo]] = 'Europe/Paris', plus: Union[str, int, float] = 0, minus: Union[str, int, float] = 0) -> datetime:
    """Provide now for given time zone, plus given time forwarded to add_time(2)"""
    d = datetime.now() if zone is None else datetime.now(zone if isinstance(zone, ZoneInfo) else ZoneInfo(zone))
    if plus or minus:
        d = add_time(d, plus, minus)
    return d

def now_ts(*, zone: Optional[Union[str, ZoneInfo]] = 'Europe/Paris') -> float:
    return now(zone=zone).timestamp()

def now_plus(*, zone: Optional[Union[str, ZoneInfo]] = 'Europe/Paris', **kwargs) -> datetime:
    return now(zone=zone) + datetime_mod.timedelta(**kwargs)

def is_today(dt: datetime) -> bool:
    return dt.strftime('%Y/%m/%d') == now(zone=zone_info_from(dt)).strftime('%Y/%m/%d')

def parse_date(s: str) -> datetime:
    "Tries to parse a date in given string ; SLOW ; NOT THREAD SAFE"
    for tmp_date in ['%A %d %B %Y', '%d %B %Y', '%B %d %Y', '%A %d %B %Y']:
        for tmp_time in ['%H:%M', '%H:%M:%S', '%Hh%M', '%Hh%Mm', '%Hh%Mm%S', '%Hh%Mm%Ss']:
            for sep in [' ', 'T', ' à ', ' at ', ' le ']:
                for tmp in [tmp_date, tmp_date + sep + tmp_time, tmp_time + sep + tmp_date]:
                    for lcl in [('fr_FR', 'UTF-8'), ('en_US', 'UTF-8')]:
                        try:
                            return datetime.strptime(s, tmp)
                        except ValueError:
                            try:
                                return localized_strptime(s, tmp, lcl)
                            except ValueError:
                                pass
    raise ValueError(f"Cannot parse given date `{s}`")

def date_from_object(obj: Union[tuple[int, int, int], date]) -> date:
    "try to return a date object"
    if isinstance(obj, date):
        return obj
    if isinstance(obj, tuple) and len(obj) == 3:
        return date(*obj)
    raise ValueError(f"Cannot extract a date object from given object {repr(obj)}")
