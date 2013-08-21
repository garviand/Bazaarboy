from django import template

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
    if False:
        pass
    # See if the end time is within 12 hours of the start time
    gap = endTime - startTime
    return 0 < gap.total_seconds() < 60 * 60 * 12

