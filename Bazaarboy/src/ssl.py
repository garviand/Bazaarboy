from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class SecureRequiredMiddleware(object):
    """
    A middleware to enforce https on all requests
    """
    def __init__(self):
        self.enabled = settings.ENFORCE_HTTPS

    def process_request(self, request):
        if (self.enabled and 
            (not request.is_secure() or 
             not request.META.get('HTTP_X_FORWARDED_PROTO', '') == 'https')):
            requestUrl = request.build_absolute_uri(request.get_full_path())
            secureUrl = requestUrl.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(secureUrl)
        return None