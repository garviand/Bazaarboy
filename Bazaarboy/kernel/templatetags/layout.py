from django import template
from django.utils import timezone
from django.core.urlresolvers import reverse
from kernel.models import *
from src.timezone import localize
import math
import re

import pdb

register = template.Library()

@register.filter
def subtract(value, arg):
    return arg - value

@register.filter
def multiply(value, arg):
    return arg * value

@register.filter
def firstImage(event):
    if event.cover:
        return event.cover.source.url.split("?", 1)[0]
    pat = re.compile('<img [^>]*src="([^"]+)')
    images = pat.findall(event.description)
    if len(images) > 0:
        return images[0].split("?", 1)[0]
    else:
        return False

@register.filter
def channelUrl(profile):
    """
    Only works on production, return subdomain + url for profile's channel
    """
    channel_url = False
    if Channel.objects.filter(profile = profile).exists():
        channel = Channel.objects.get(profile = profile)
        if channel.slug:
            channel_url = 'https://' + channel.slug + '.bazaarboy.com'
    return channel_url

@register.filter
def daysUntil(value):
    now = timezone.now()
    diff  = value - now
    if diff.days > 0:
        return str(diff.days) + ' days'
    else:
        return str(diff.seconds//3600) + ' hours'

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
    return time.strftime('%m/%d/%Y').lstrip('0') + ' @ ' + time.strftime('%I:%M%p').lstrip('0') if time is not None else ''

@register.filter
def standardDate(event):
    """
    Output a nicely formatted date for an event
    """
    startTime = localize(event.start_time)
    if event.end_time:
        endTime = localize(event.end_time)
        if endTime.day == startTime.day:
            event_date = startTime.strftime('%A') + ', ' + startTime.strftime('%B') + ' ' + startTime.strftime('%d').lstrip('0') + ', '
            event_date += startTime.strftime('%I:%M%p').lower() + ' - ' + endTime.strftime('%I:%M%p').lower().lstrip('0')
        else:
            event_date = startTime.strftime('%A') + ', ' + startTime.strftime('%B') + ' ' + startTime.strftime('%d').lstrip('0') + ', ' + startTime.strftime('%I:%M%p').lower().lstrip('0') + ' - '
            event_date += endTime.strftime('%A') + ', ' + startTime.strftime('%B') + ' ' + startTime.strftime('%d').lstrip('0') + ', ' + endTime.strftime('%I:%M%p').lower().lstrip('0')
    else:
        event_date = startTime.strftime('%A') + ', ' + startTime.strftime('%B') + ' ' + startTime.strftime('%d').lstrip('0') + ', '
        event_date += startTime.strftime('%I:%M%p').lower().lstrip('0')
    return event_date

@register.filter
def validateTiming(obj):
    """
    Validate an object to make sure it has started and hasn't ended
    """
    if obj.start_time:
        if obj.end_time:
            return obj.start_time <= timezone.now() and obj.end_time > timezone.now()
        else:
            return obj.start_time <= timezone.now()
    else:
        if obj.end_time:
            return obj.end_time > timezone.now()
        else:
            return True

@register.filter
def ticketSaleTiming(ticket):
    if ticket.end_time and ticket.end_time < timezone.now():
        return "Ticket sale has ended"
    if ticket.start_time and ticket.start_time >= timezone.now():
        return "Ticket is not on sale yet"
    return "Ticket is not on sale"

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
        return reverse('event-slug', kwargs = {'id': event.slug})
    return reverse('event:index', kwargs = {'id': event.id})

@register.filter
def sanitizeUrl(url):
    """
    Strip the parameters from the url
    """
    return url.split('?')[0]

@register.filter
def facebookProfile(fullURL):
    """
    Get Facebook Profile From URL
    """
    return fullURL.split(".com/")[1]

@register.filter
def phoneDisplay(number):
    """
    Pretty Phone Number Display
    """
    return number[0:3] + "&nbsp;&middot;&nbsp;" + number[3:6] + "&nbsp;&middot;&nbsp;" + number[6:10]