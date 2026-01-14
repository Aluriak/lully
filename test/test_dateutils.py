import re
import pytest
import lully as ll
import datetime
from lully.dateutils import now, now_plus


def comparable(d: datetime.datetime) -> float:
    return round(d.timestamp(), 1)


def test_now_plus_time():
    t = now()
    t_plus_1000 = comparable((t + datetime.timedelta(seconds=1000)))
    assert round(t.timestamp() + 1000, 1) == t_plus_1000
    assert t_plus_1000 == round(now_plus(seconds=1000).timestamp(), 1)

def test_now_awareness():
    assert     ll.dt_is_aware(now())
    assert not ll.dt_is_naive(now())
    assert not ll.dt_is_aware(datetime.datetime.now())
    assert     ll.dt_is_naive(datetime.datetime.now())

def test_now_plus_string_time():
    assert comparable(now(plus='1000s')) == comparable(now_plus(seconds=1000))
    assert comparable(now(plus='1000s')) == comparable(now(plus=1000))
    assert comparable(now(plus='1w')) == comparable(now(plus='7d'))
    assert comparable(now(plus='-60S')) == comparable(now(plus='-1m'))
    assert comparable(now(zone='America/Martinique', plus='-1d')) == comparable(now_plus(zone='America/Martinique', days=-1))

def test_minus():
    assert comparable(now(plus='1000s', minus='1000s')) == comparable(now())
    assert ll.dateutils.time_from_now(now(plus='50s', minus='109s')) == '59 secondes'


def test_time_since():
    one_day_ago = now(plus='-1d')
    assert ll.time_since(one_day_ago) == "1 jour"
    assert ll.time_since(one_day_ago, ref=one_day_ago) == "À l'instant"
    assert ll.time_since(one_day_ago.timestamp()) == "1 jour"

def test_merdier_utc():
    """Erreur trouvée depuis (sans doute) le changement d'heure, avec les tokens
    du vault qui ont des dates de la forme 2024-11-20T15:52:26.514695222+01:00,
    ce qui était visiblement inattendu.

    Du coup, on a hardcodé le passage de UTC+1 à Europe/Paris. On verra si ça suffit.
    """
    dt = datetime.datetime.fromisoformat('2024-11-20 19:21:18.848482+01:00')
    print(dt, type(dt))
    from zoneinfo import ZoneInfo
    zi = ll.dateutils.zone_info_from(dt)
    assert isinstance(zi, ZoneInfo)
    assert ll.time_since(dt) and isinstance(ll.time_since(dt), str)

def test_change_tz():
    dt = datetime.datetime.fromisoformat('2026-01-01 12:00:00.000000+01:00')
    dt_paque = ll.dateutils.change_tz(dt, to='Chile/EasterIsland')
    assert dt == datetime.datetime.fromisoformat('2026-01-01 12:00:00.000000+01:00')  # dt has not been changed
    assert dt == dt_paque  # same date, different location
    assert ll.dateutils.time_since(dt) == ll.dateutils.time_since(dt_paque)
    assert dt.strftime('%I:%M%p') != dt_paque.strftime('%I:%M%p')


def test_aware_of_awareness():
    assert ll.time_since(now(zone='America/Martinique', minus='15d')) == '2 semaines et 1 jour'
    assert ll.time_since(now(zone='America/Martinique',  plus='-15d'), precision=1) == '2 semaines'
    assert ll.time_since(datetime.datetime.now()) == "À l'instant"

    assert ll.time_since(now(zone='America/Chicago', plus='-15d')) == '2 semaines et 1 jour'
    assert ll.time_since(now(zone='Europe/Moscow', plus='-15d'), precision=1) == '2 semaines'

def test_aware_of_utc():
    assert ll.dt_is_aware(datetime.datetime.now(datetime.timezone.utc))
    assert ll.time_since(datetime.datetime.now(datetime.timezone.utc)) == "À l'instant"

    # note that utcnow returns a naive dt
    assert ll.dt_is_naive(datetime.datetime.utcnow())

    assert (
        ll.time_since(datetime.datetime.utcnow()) == '2 heures'  # heure d'été
     or ll.time_since(datetime.datetime.utcnow()) == '1 heure'  # heure d'hiver
    )

def test_is_today():
    assert ll.dateutils.is_today(datetime.datetime.now(datetime.timezone.utc))
    assert not ll.dateutils.is_today(ll.dateutils.now(minus='-1d'))

    now = ll.dateutils.now()
    assert ll.dateutils.is_today(ll.dateutils.first_time_of_day(now))
    assert ll.dateutils.is_today(ll.dateutils.last_time_of_day(now))

    assert not ll.dateutils.is_today(ll.dateutils.first_time_of_day(now) - datetime.timedelta(seconds=1))
    assert not ll.dateutils.is_today(ll.dateutils.last_time_of_day(now) + datetime.timedelta(seconds=1))


def test_parse_date():
    assert ll.dateutils.parse_date('Mardi 02 Mars 2025').strftime('%Y/%m/%d') == '2025/03/02'
    assert ll.dateutils.parse_date('mardi 2 mars 2025').strftime('%Y/%m/%d') == '2025/03/02'
    assert ll.dateutils.parse_date('2 mars 2025').strftime('%Y/%m/%d') == '2025/03/02'
    assert ll.dateutils.parse_date('march 02 2025').strftime('%Y/%m/%d') == '2025/03/02'
    assert ll.dateutils.parse_date('march 02 2025 at 11:03').strftime('%Y/%m/%d %H:%M:%S') == '2025/03/02 11:03:00'
    assert ll.dateutils.parse_date('11:03 le 2 mars 2025').strftime('%Y/%m/%d %H:%M:%S') == '2025/03/02 11:03:00'
    with pytest.raises(ValueError):
        ll.dateutils.parse_date('not a date')

def test_parse_microseconds():
    parse = ll.dateutils.parse_isoformat_with_microseconds
    assert parse('2023-12-15T14:10:47.717263573+01:00') == datetime.datetime(2023, 12, 15, 14, 10, 47, 717263, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))
    assert parse('2023-12-15T14:10:47.0717263573+01:00') == datetime.datetime(2023, 12, 15, 14, 10, 47, 71726, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))
    assert parse('2025-04-02T11:04:04.83599+02:00') == datetime.datetime(2025, 4, 2, 11, 4, 4, 835990, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))


def test_regex_parse_date():
    dates = (
        '2025-04-02T11:10:14.83599+02:00',
        '2025-04-02T11:10:14.8359+02:00',
        '2025-04-02T11:10:14.835+02:00',
    )
    for d in dates:
        r = ''.join(re.fullmatch(ll.dateutils.REGEX_DATETIME_MATCH, d).groups())  # type: ignore[union-attr]
        assert r == d
