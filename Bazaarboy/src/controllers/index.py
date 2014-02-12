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
    pids = []
    for profile in profiles:
        pids.append(profile.id)
    # If user doesn't have a profile, redirect to profile creation
    if profiles.count() is 0:
        return redirect('profile:new')
    # Fetch events
    currentEvents = Event.objects.filter(Q(end_time = None, 
                                           start_time__gt = tz.now()) | 
                                         Q(end_time__isnull = False, 
                                           end_time__gt = tz.now()),   
                                         is_launched = True, 
                                         organizers__in = pids) \
                                 .order_by('start_time')
    currentEventsCount = currentEvents.count()
    currentEvents = currentEvents[:5]
    pastEvents = Event.objects.filter(Q(end_time = None, 
                                        start_time__lt = tz.now()) | 
                                      Q(end_time__isnull = False, 
                                        end_time__lt = tz.now()), 
                                      is_launched = True, 
                                      organizers__in = pids) \
                              .order_by('-start_time')[:5]
    pastEventsCount = pastEvents.count()
    pastEvents = currentEvents[:5]
    draftEvents = Event.objects.filter(is_launched = False, 
                                       organizers__in = pids)
    draftEventsCount = draftEvents.count()
    draftEvents = draftEvents[:5]
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

def pageNotFound(request):
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