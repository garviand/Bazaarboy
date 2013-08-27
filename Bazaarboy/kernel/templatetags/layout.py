from django import template
from src.timezone import localize

register = template.Library()

@register.filter
def split(value, delimiter):
    """
    Split a value by a dilimiter and return the parts
    """
    return value.split(delimiter)

@register.filter
def shouldShortenEndTime(endTime, startTime):
    """
    Determin whether to shorten the end time
    """
    # Make sure the two values are not null
    if endTime is None or startTime is None:
        return False
    # See if the two are on the same day
    endTime = localize(endTime)
    startTime = localize(startTime)
    return endTime.day == startTime.day

@register.filter
def standardTime(time):
    """
    Output a datetime object to text in standard format
    """
    time = localize(time)
    return time.strftime('%Y-%m-%d %X') if time is not None else ''