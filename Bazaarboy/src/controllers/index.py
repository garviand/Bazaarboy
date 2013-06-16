"""
Controller for index
"""

from django.shortcuts import render
from request import validate

@validate('GET', [], ['next'])
def index(request, params):
    """
    Index page
    """
    if not request.session.has_key('user'):
        # If there is no session, show landing page
        return render(request, 'landing.html', locals())
    return render(request, 'index.html', locals())