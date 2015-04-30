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
from kernel.templatetags import layout
from src.config import *
from src.controllers.request import validate, login_check, json_response
from instagram.client import InstagramAPI

from subdomains.utils import get_domain

import pdb

@never_cache
@login_check()
@validate('GET', [], ['next'])
def index(request, params, user):
    """
    Index page
    """
    if request.subdomain is not None and request.subdomain not in ['www']:
        subdomain = request.subdomain
        if Channel.objects.filter(slug = subdomain, active = True).exists():
            channel = Channel.objects.get(slug = subdomain)
            profile = channel.profile
            organizers = Organizer.objects.filter(profile = profile, event__is_launched = True, event__is_deleted = False, event__is_private = False).order_by('-event__start_time')
            current_events = []
            past_events = []
            for organizer in organizers:
                if layout.firstImage(organizer.event):
                    if not layout.hasStartedOrEnded(organizer.event):
                        current_events.append(organizer.event)
                    else:
                        past_events.append(organizer.event)
            current_events.reverse()
            past_events = past_events[:9]
            api = InstagramAPI(client_id=INSTAGRAM_CLIENT_ID, client_secret=INSTAGRAM_SECRET)
            instagram_photos = api.tag_recent_media(count=10, tag_name=str(channel.hashtag))
            images = []
            for photo in instagram_photos[0]:
                images.append({'high_res':photo.images['standard_resolution'].url, 'thumb':photo.images['thumbnail'].url})
            images = images[:9]
            return render(request, 'profile/index.html', locals())
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
    # Lists
    profile = profiles[0]
    lists = List.objects.filter(owner = profiles[0], is_deleted = False)
    for lt in lists:
        list_items = List_item.objects.filter(_list = lt)
        lt.items = list_items.count()
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
    pastEvents = pastEvents.filter()[:30]
    pastEvents = list(pastEvents)
    pastEventsAttention = []
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
        current_organizer = Organizer.objects.get(event__id = pastEvents[i].id, profile__in = pids)
        if Recap.objects.filter(organizer = current_organizer, is_viewed = False).exists():
            pastEventsAttention.append(pastEvents[i])
    pastEventsAttentionCount = len(pastEventsAttention)
    draftEvents = Event.objects.filter(is_launched = False,
                                       is_deleted = False,
                                       organizers__in = pids).order_by('-id')
    draftEventsCount = draftEvents.count()
    draftEvents = draftEvents.filter()[:100]
    for i in range(0, len(draftEvents)):
        draftEvents[i].creator = True
        if not Organizer.objects.filter(event = draftEvents[i], profile__managers = user, is_creator = True).exists():
            draftEvents[i].creator = False
    collaboration_requests = Collaboration_request.objects.filter(profile__in = pids, accepted__isnull = True, is_rejected = False).exclude(event__organizer__profile__in = pids)
    active_rewards = Reward_item.objects.filter(reward__creator__managers = user, expiration_time__gte = tz.now())
    reward_list = []
    for reward in active_rewards:
        if not reward.reward in reward_list:
            reward.reward.claims = len(Claim.objects.filter(item__reward = reward.reward, is_claimed = True))
            reward.reward.redemptions = len(Claim.objects.filter(item__reward = reward.reward, is_redeemed = True))
            reward_list.append(reward.reward)
    newSignups = Sign_up_item.objects.filter(Q(sign_up__owner__in = pids) | Q(profile__in = pids), assigned = False)
    return render(request, 'index/index.html', locals())

@login_check()
@validate('GET', [], ['next', 'code', 'requestid', 'requestc', 'rewid', 'rewtok', 'rewardreqid'])
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
        if params['rewid'] and params['rewtok']:
            if Reward_send.objects.filter(id = params['rewid'], token = params['rewtok']).exists():
                reward_send = Reward_send.objects.get(id = params['rewid'])
        if params['rewardreqid'] and params['requestc']:
            if Reward_request.objects.filter(id = params['rewardreqid'], code = params['requestc']).exists():
                reward_request = Reward_request.objects.get(id = params['rewardreqid'])

        return render(request, 'index/login.html', locals())

@login_check()
@validate('GET', [], ['next', 'code', 'requestid', 'requestc', 'rewid', 'rewtok', 'sem', 'rewardreqid'])
def register(request, user, params):
    """
    Register Page
    """
    if user:
        return redirect('index')
    else:
        if params['sem']:
            prepopulated_email = params['sem']
        if params['next']:
            next = params['next']
        if params['code']:
            code = params['code']
        if params['requestid'] and params['requestc']:
            if Collaboration_request.objects.filter(id = params['requestid'], code = params['requestc']).exists():
                organizer_request = Collaboration_request.objects.get(id = params['requestid'], code = params['requestc'])
        if params['rewid'] and params['rewtok']:
            if Reward_send.objects.filter(id = params['rewid'], token = params['rewtok']).exists():
                reward_send = Reward_send.objects.get(id = params['rewid'])
        if params['rewardreqid'] and params['requestc']:
            if Reward_request.objects.filter(id = params['rewardreqid'], code = params['requestc']).exists():
                reward_request = Reward_request.objects.get(id = params['rewardreqid'])
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
    request.session['django_timezone'] = params['timezone']
    return json_response({})