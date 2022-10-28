import datetime
import re
from typing import Union


def parse_duration(duration: str) -> Union[datetime.timedelta, None]:
    """
    Parse duration from text form to datetime.time()

    Formats:
    <Number><Unit>
    <Number> <Unit>

    Examples:
        5m
        10 m
        3m 15s
    """

    hours = minutes = seconds = 0
    res = re.findall('([1-9][0-9]*) *([smh])', duration)

    try:
        for value, unit in res:
            if unit == 'm':
                minutes += float(value)
            elif unit == 'h':
                hours += float(value)
            elif unit == 's':
                seconds += float(value)
    except TypeError:
        return None

    return datetime.timedelta(hours=hours, seconds=seconds, minutes=minutes)
