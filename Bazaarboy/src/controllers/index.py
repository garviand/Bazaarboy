"""
Controller for index
"""

import pytz
import urllib
from datetime import timedelta
from django.db.models import Q, Sum, Count
from django.shortcuts import render, redirect
from django.utils import timezone as tz
from django.views.decorators.cache import never_cache
from kernel.models import *
from src.config import *
from src.controllers.request import validate, login_check, json_response

@never_cache
@login_check()
@validate('GET', [], ['next'])
def index(request, params, user):
    """
    Index page
    """
    # Check if logged in
    if user is None:
        return render(request, 'index/landing.html', locals())
    # Fetch profiles managed by the user
    profiles = Profile.objects.filter(managers = user)
    # If user doesn't have a profile, redirect to profile creation
    if profiles.count() is 0:
        return redirect('profile:new')
    return render(request, 'index/index.html', locals())

@login_check()
def terms(request, user):
    """
    Terms of services
    """
    return render(request, 'index/terms.html', locals())

@login_check()
def pricing(request, user):
    """
    Pricing & Info
    """
    return render(request, 'index/pricing.html', locals())

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