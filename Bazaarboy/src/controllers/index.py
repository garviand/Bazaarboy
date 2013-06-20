"""
Controller for index
"""

from django.shortcuts import render
from request import validate, login_check

@login_check()
@validate('GET', [], ['next'])
def index(request, params, loggedIn):
    """
    Index page
    """
    if not loggedIn:
        return render(request, 'landing.html', locals())
    return render(request, 'index.html', locals())