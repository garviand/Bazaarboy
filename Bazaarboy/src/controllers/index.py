"""
Controller for index
"""

from django.shortcuts import render
from src.controllers.request import validate, login_check

@login_check()
@validate('GET', [], ['next'])
def index(request, params, loggedIn):
    """
    Index page
    """
    if not loggedIn:
        return render(request, 'index/landing.html', locals())
    return render(request, 'index/index.html', locals())

def terms(request):
    pass

def about(request):
    pass

@login_check()
def pageNotFound(request, loggedIn):
    return render(request, '404.html', locals())

def serverError(request):
    return render(request, '500.html', locals())