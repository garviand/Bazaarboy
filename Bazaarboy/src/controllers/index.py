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
    # Count events
    eventsCount = Event.objects.filter(is_deleted = False, organizers__in = pids).count()
    # Fetch events
    currentEvents = Event.objects.filter(Q(end_time = None, 
                                           start_time__gt = tz.now()) | 
                                         Q(end_time__isnull = False, 
                                           end_time__gt = tz.now()),   
                                         is_launched = True, 
                                         organizers__in = pids) \
                                 .order_by('start_time')
    currentEventsCount = currentEvents.count()
    currentEvents = list(currentEvents)
    for i in range(0, len(currentEvents)):
        currentEvents[i].creator = True
        if not Organizer.objects.filter(event = currentEvents[i], profile__managers = user, is_creator = True).exists():
            currentEvents[i].creator = False
        stats = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = currentEvents[i])
        totalSale = stats.aggregate(Sum('amount'))['amount__sum']
        totalRSVP = stats.aggregate(Count('items'))['items__count']
        currentEvents[i].totalSale = totalSale
        if currentEvents[i].totalSale is None:
            currentEvents[i].totalSale = 0
        currentEvents[i].rsvpCount = totalRSVP
        tickets = Ticket.objects.filter(event = currentEvents[i], 
                                        is_deleted = False)
        potentialQuantity = 0
        potentialSale = 0
        for ticket in tickets:
            if ticket.price > 0 and ticket.quantity is None:
                potentialQuantity = None
                potentialSale = None
                break
            if ticket.quantity is not None:
                if potentialQuantity is not None:
                  potentialQuantity += ticket.quantity
                potentialSale += ticket.price * ticket.quantity
            else:
                potentialQuantity = None
        currentEvents[i].potentialQuantity = potentialQuantity
        if potentialQuantity:
            currentEvents[i].potentialQuantity += totalRSVP
        currentEvents[i].potentialSale = potentialSale
    pastEvents = Event.objects.filter(Q(end_time = None, 
                                        start_time__lt = tz.now()) | 
                                      Q(end_time__isnull = False, 
                                        end_time__lt = tz.now()), 
                                      is_launched = True, 
                                      organizers__in = pids) \
                              .order_by('-start_time')
    pastEventsCount = pastEvents.count()
    pastEvents = pastEvents.filter()[:10]
    pastEvents = list(pastEvents)
    for i in range(0, len(pastEvents)):
        pastEvents[i].creator = True
        if not Organizer.objects.filter(event = pastEvents[i], profile__managers = user, is_creator = True).exists():
            pastEvents[i].creator = False
        stats = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = pastEvents[i])
        totalSale = stats.aggregate(Sum('amount'))['amount__sum']
        totalRSVP = stats.aggregate(Count('items'))['items__count']
        pastEvents[i].totalSale = totalSale
        pastEvents[i].rsvpCount = totalRSVP
        tickets = Ticket.objects.filter(event = pastEvents[i], 
                                        is_deleted = False)
        potentialQuantity = 0
        potentialSale = 0
        for ticket in tickets:
            if ticket.price > 0 and ticket.quantity is None:
                potentialQuantity = None
                potentialSale = None
                break
            if ticket.quantity is not None:
                if potentialQuantity is not None:
                  potentialQuantity += ticket.quantity
                potentialSale += ticket.price * ticket.quantity
            else:
                potentialQuantity = None
        pastEvents[i].potentialQuantity = potentialQuantity
        if potentialQuantity:
            pastEvents[i].potentialQuantity += totalRSVP
        pastEvents[i].potentialSale = potentialSale
    draftEvents = Event.objects.filter(is_launched = False,
                                       is_deleted = False,
                                       organizers__in = pids)
    draftEventsCount = draftEvents.count()
    draftEvents = draftEvents.filter()[:10]
    collaboration_requests = Collaboration_request.objects.filter(profile__in = pids, accepted__isnull = True, is_rejected = False).exclude(event__organizer__profile__in = pids)
    return render(request, 'index/index.html', locals())

@login_check()
@validate('GET', [], ['next', 'code', 'requestid', 'requestc'])
def login(request, user, params):
    """
    Login Page
    """
    if user:
        return redirect('index')
    else:
        if params['next']:
            next = params['next']
        if params['code']:
            code = params['code']
        if params['requestid'] and params['requestc']:
            if Collaboration_request.objects.filter(id = params['requestid'], code = params['requestc']).exists():
                organizer_request = Collaboration_request.objects.get(id = params['requestid'], code = params['requestc'])
        return render(request, 'index/login.html', locals())

@login_check()
@validate('GET', [], ['next', 'code', 'requestid', 'requestc'])
def register(request, user, params):
    """
    Register Page
    """
    if user:
        return redirect('index')
    else:
        if params['next']:
            next = params['next']
        if params['code']:
            code = params['code']
        if params['requestid'] and params['requestc']:
            if Collaboration_request.objects.filter(id = params['requestid'], code = params['requestc']).exists():
                organizer_request = Collaboration_request.objects.get(id = params['requestid'], code = params['requestc'])
        return render(request, 'index/register.html', locals())

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