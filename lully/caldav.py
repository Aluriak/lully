
import caldav
import lully as ll
from typing import Union
from datetime import date


def add_birthday(name, birthdate: Union[tuple[int, int, int], date], *, minage: int = 0, maxage: int = 120, url: str, usr: str, pwd: str, calid: str, title_template: str = "{name} ({N} yo)", description_template: str = "Today is the {N}th birthday of {name}"):
    """Add a birthday event (or events, see below) for given name, every year for `maxage` years after birth (120 by default).

    Will create either one yearly created event (if title or description doesn't involve the use of {N} years old)
    or one event per birthday (to show how old is the birthdayed person, this is the default behavior).

    UNTESTED: caldav API is probably misused

    """

    recurring_event = '{N}' not in title_template and '{N}' not in description_template  # we can't use yearly recurring event if we have to show age in title or description of each event
    birthdate = ll.dateutils.date_from_object(birthdate)

    events = []  # list of created events
    with caldav.DAVClient(url=ll.url.with_scheme(url), username=usr, password=pwd) as client:
        # Operations with the client object
        principal = client.principal()
        calendar = principal.calendar(cal_id=calid)

        create_event = lambda N: calendar.save_event(
            summary=title_template.format(N=N, name=name),
            description=description_template.format(N=N, name=name),
            dtstart=date(birthdate.year + N, birthdate.month, birthdate.day),
            # dtend=datetime(2023, 5, 17, 10, 0),
            rrule={"FREQ": "YEARLY", "COUNT": maxage-N} if recurring_event else {}
        )

        for N in range(minage, (minage if recurring_event else maxage+1)):
            events.append(create_event(N))
    return events
