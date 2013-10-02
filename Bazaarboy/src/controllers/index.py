"""
Controller for index
"""

import pytz
from django.shortcuts import render, redirect
from src.controllers.request import validate, login_check, json_response

@login_check()
@validate('GET', [], ['next'])
def index(request, params, user):
    """
    Index page
    """
    if user is None:
        return render(request, 'index/landing.html', locals())
    return render(request, 'index/index.html', locals())

@login_check()
def terms(request, user):
    """
    Terms of services
    """
    return render(request, 'index/terms.html', locals())

@login_check()
def about(request, user):
    pass

@login_check()
def pageNotFound(request, user):
    return render(request, '404.html', locals())

def serverError(request):
    return render(request, '500.html', locals())

@validate('POST', ['timezone'])
def timezone(request, params):
    """
    Set timezone info for this session
    """
    request.session['django_timezone'] = pytz.timezone(params['timezone'])
    return json_response({})