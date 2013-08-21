"""
A module that deals with timezone issues
"""

from django.utils import timezone

class TimezoneMiddleware(object):
    """
    A middleware that activates timezone info for requests
    """
    def process_request(self, request):
        """
        Add timezone info to request context
        """
        tz = request.session.get('django_timezone')
        if tz:
            timezone.activate(tz)

def localize(time):
    """
    Localize a datetime using current timezone
    """
    time = time.astimezone(timezone.get_current_timezone())
    time = timezone.get_current_timezone().normalize(time)
    return time