from django import template
from django.utils import timezone
from django.core.urlresolvers import reverse
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
def isOnSaleSoon(ticket):
    """
    Check if a ticket is on sale soon or its sale period has ended
    """
    return ticket.start_time > timezone.now()

@register.filter
def hasStartedOrEnded(obj):
    """
    Check if an event is still valid for ticketing
    """
    return ((obj.end_time is None and obj.start_time <= timezone.now()) or 
            (obj.end_time is not None and timezone.now() >= obj.end_time))

@register.filter
def eventUrl(event):
    """
    Return Slug or Event ID when appropriate
    """
    if event.slug:
        return reverse('event-slug', kwargs={'id': event.slug})
    else:
        return reverse('event:index', kwargs={'id': event.id})

@register.filter
def sanitizeUrl(url):
    """
    Strip the parameters from the url
    """
    return url.split('?')[0]