# Taken from https://gist.github.com/spatialtime/c1924a3b178b4fe721fe406e0bf1a1dc

# This snippet demonstrates Pythonic formatting and parsing of 
# ISO 8601 durations.
# A little work is required to navigate between Python's
# timedelta syntax and ISO 8601 duration syntax.

import re

from datetime import datetime
from datetime import timedelta

def format_duration(td):
    """Formats a timedelta instance into a correct ISO 8601 duration string.

    Args:
        td: a datetime.timedelta instance.
    Returns:
        a ISO 8601 duration string.
    """
    
    s = td.seconds 
    
    ms = td.microseconds
    if ms != 0:  # Round microseconds to milliseconds.
        ms /= 1000000
        ms = round(ms,3)
        s += ms
        
    return "P{}DT{}S".format(td.days,s)

def parse_duration(iso_duration):
    """Parses an ISO 8601 duration string into a datetime.timedelta instance.

    Args:
        iso_duration: an ISO 8601 duration string.
    Returns:
        a datetime.timedelta instance
    """
    m = re.match(r'^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:.\d+)?)S)?$',
        iso_duration)
    if m is None:
        raise ValueError("invalid ISO 8601 duration string")

    days = 0
    hours = 0
    minutes = 0
    seconds = 0.0

    # Years and months are not being utilized here, as there is not enough 
    # information provided to determine which year and which month.
    # Python's time_delta class stores durations as days, seconds and
    # microseconds internally, and therefore we'd have to 
    # convert parsed years and months to specific number of days.

    if m[3]:
        days = int(m[3])
    if m[4]:
        hours = int(m[4])
    if m[5]:
        minutes = int(m[5])
    if m[6]:
        seconds = float(m[6])

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


#example usage of format_duration()
td = timedelta(seconds=10.2, milliseconds=322)
iso_duration = format_duration(td)
print(iso_duration)

#example usage of parse_duration()
print(parse_duration(iso_duration))

