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
    # Fetch stripe accounts linked to the user
    paymentAccounts = user.payment_account_set.all()
    stripeConnectUrl = r'%s?response_type=code&client_id=%s&scope=%s'
    stripeConnectUrl = stripeConnectUrl % (STRIPE_CONNECT_URL, 
                                           STRIPE_CLIENT_ID, 
                                           STRIPE_SCOPE)
    # Fetch profiles managed by the user
    profiles = Profile.objects.filter(managers = user)
    profiles = list(profiles)
    for i in range(0, len(profiles)):
        profile = profiles[i]
        # Fetch the stats for the profile
        stats = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event__organizers = profile) \
                                .aggregate(total_sale = Sum('price'), 
                                           sale_count = Count('id'))
        profile.stats = stats
        # Fetch draft events
        draftEvents = Event.objects.filter(organizers = profile, 
                                           is_launched = False) \
                                   .order_by('-created_time')[:5]
        draftEvents = list(draftEvents)
        # Fetch live events
        liveEvents = Event.objects.filter(organizers = profile, 
                                          start_time__gt = tz.now(), 
                                          is_launched = True) \
                                  .order_by('start_time')[:5]
        liveEvents = list(liveEvents)
        for j in range(0, len(liveEvents)):
            # Fetch the stats for the event
            stats = Purchase.objects.filter(Q(checkout = None) | 
                                            Q(checkout__is_charged = True, 
                                              checkout__is_refunded = False), 
                                            event = liveEvents[j]) \
                                    .aggregate(total_sale = Sum('price'), 
                                               sale_count = Count('id'))
            liveEvents[j].total_sale = stats['total_sale']
            liveEvents[j].sale_count = stats['sale_count']
        # Fetch past events
        pastEvents = Event.objects.filter(organizers = profile, 
                                          start_time__lte = tz.now(), 
                                          is_launched = True) \
                                  .order_by('-start_time')[:5]
        pastEvents = list(pastEvents)
        for j in range(0, len(pastEvents)):
            # Fetch the stats for the event
            stats = Purchase.objects.filter(Q(checkout = None) | 
                                            Q(checkout__is_charged = True, 
                                              checkout__is_refunded = False), 
                                            event = pastEvents[j]) \
                                    .aggregate(total_sale = Sum('price'), 
                                               sale_count = Count('id'))
            pastEvents[j].total_sale = stats['total_sale']
            pastEvents[j].sale_count = stats['sale_count']
        # Attached the data to profile
        profile.draftEvents = draftEvents
        profile.liveEvents = liveEvents
        profile.pastEvents = pastEvents
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