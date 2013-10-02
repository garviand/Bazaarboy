from django import template
from django.utils import timezone
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

@register.filter
def validateTiming(obj):
    """
    Validate an object to make sure it has started and hasn't ended
    """
    return obj.start_time <= timezone.now() and obj.end_time > timezone.now()

@register.filter
def hasStarted(obj):
    """
    Check if an object's start_time is past now
    """
    return obj.start_time <= timezone.now()

@register.filter
def sanitizeUrl(url):
    """
    Strip the parameters from the url
    """
    return url.split('?')[0]