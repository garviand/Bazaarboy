"""
Controller for events
"""

import cgi
import json
import simplejson
import os
import re
import ordereddict
from dateutil import parser
from datetime import timedelta
from django.db import transaction, IntegrityError
from django.db.models import F, Q, Count, Sum
from django.http import Http404
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.views.decorators.cache import cache_page
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.serializers.json import DjangoJSONEncoder
from celery import task
from kernel.models import *
from kernel.templatetags import layout
from src.config import *
from src.controllers.request import *
from src.ordereddict import OrderedDict
from src.csvutils import UnicodeWriter
from src.email import sendEventConfirmationEmail, sendEventInvite, sendManualEventInvite, sendOrganizerAddedEmail, sendIssueEmail, sendEventReminder, sendRecapReminder, sendCollaborationRequest, sendCollaborationResponse, sendFollowUp
from src.regex import REGEX_EMAIL, REGEX_NAME, REGEX_SLUG
from src.sanitizer import sanitize_redactor_input
from src.serializer import serialize, serialize_one
from src.sms import sendEventConfirmationSMS
from mandrill import Mandrill
import logging
from instagram.client import InstagramAPI

import pdb
import operator

@cache_page(60 * 5)
@login_check()
@validate('GET', [], ['preview', 'design', 'iid'])
def index(request, id, params, user):
    """
    Event page
    """
    event = None
    if id.isdigit() and Event.objects.filter(id = id, is_deleted = False).exists():
        event = Event.objects.select_related().get(id = id)
    elif Event.objects.filter(slug = id, is_deleted = False).exists():
        event = Event.objects.select_related().get(slug = id)
    if event is None:
        raise Http404
    editable = (user is not None and 
                Organizer.objects.filter(event = event, 
                                         profile__managers = user, is_creator = True).exists())
    collab_invite_pending = Collaboration_request.objects.filter(event = event, profile__managers = user).exists()
    preview = params['preview'] is not None and (editable or collab_invite_pending)
    design = params['design'] is not None and editable
    if not design and not preview and not event.is_launched:
        return redirect('index')
    pastEventList = {}
    if editable:
        profiles = Profile.objects.filter(managers = user)
        pids = []
        for profile in profiles:
            pids.append(profile.id)
        pastEvents = Event.objects.filter(Q(end_time = None, 
                                            start_time__lt = timezone.now()) | 
                                          Q(end_time__isnull = False, 
                                            end_time__lt = timezone.now()), 
                                          is_launched = True, 
                                          organizers__in = pids) \
                                  .order_by('-start_time')
        eids = []
        for pastEvent in pastEvents:
            eids.append(pastEvent.id)
        purchases = Purchase.objects.filter(Q(checkout = None) | 
                                    Q(checkout__is_charged = True, 
                                      checkout__is_refunded = False), 
                                    event__in = eids, 
                                    is_expired = False)
        for purchase in purchases:
            if purchase.event.id in pastEventList:
                pastEventList[purchase.event.id]['quantity'] += 1
            else:
                pastEventList[purchase.event.id] = {
                    'id': purchase.event.id,
                    'name': purchase.event.name,
                    'quantity': 1
                }
    tickets = Ticket.objects.filter(event = event, is_deleted = False).order_by('order', '-id')
    requiresAddress = False
    for ticket in tickets:
        if ticket.request_address:
            requiresAddress = True
        if ticket.extra_fields:
            custom_fields = simplejson.loads(ticket.extra_fields, object_pairs_hook=ordereddict.OrderedDict)
            fields = ordereddict.OrderedDict()
            for field_name, field_options in custom_fields.iteritems():
                fields[field_name] = []
                if field_options.strip() != '':
                    for option in field_options.split(','):
                        fields[field_name].append(option.strip())
            ticket.custom_fields = fields
    promos = Promo.objects.filter(event = event, is_deleted = False)
    organizers = Organizer.objects.filter(event = event)
    rsvp = True
    cheapest = float('inf')
    hasEnded = False
    if event.end_time:
        if event.end_time < timezone.now():
            hasEnded = True
    else:
        if event.start_time < timezone.now():
            hasEnded = True
    for ticket in tickets:
        if ticket.price > 0:
            rsvp = False
        if ticket.price < cheapest:
            cheapest = ticket.price
    if params['iid'] is not None and params['iid'].isdigit():
        if Invite.objects.filter(id = params['iid']).exists():
            invite = Invite.objects.get(id = params['iid'])
    return render(request, 'event/index.html', locals())

@login_required()
@validate('GET', [], ['create'])
def modify(request, id, step, params, user):
    """
    Modify/create event flow
    """
    if not Event.objects.filter(id = id, is_deleted = False).exists():
        raise Http404
    event = Event.objects.select_related().get(id = id)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user, is_creator = True).exists():
        return redirect('index')
    tzChoices = TIME_ZONE_CHOICES
    if step == 'tickets':
        tickets = Ticket.objects.filter(event = event, is_deleted = False).order_by('order')
        cheapest = float('inf')
        for ticket in tickets:
            if ticket.price < cheapest:
                cheapest = ticket.price
        tickets = list(tickets)
        ticketCount = len(tickets)
        ticketExists = ticketCount > 0
        for i in range(0, ticketCount):
            sold = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                                Q(purchase__checkout__is_charged = True, 
                                                  purchase__checkout__is_refunded = False), 
                                                ticket = tickets[i]).count()
            tickets[i].sold = sold
        promos = Promo.objects.filter(event = event, is_deleted = False).order_by('-id')
        for promo in promos:
            if Purchase_promo.objects.filter(promo = promo).exists():
                amount_claimed = Purchase_promo.objects.filter(promo = promo).aggregate(Sum('quantity'))['quantity__sum']
                promo.claimed = amount_claimed
            else:
                promo.claimed = 0
    return render(request, 'event/modify-' + step + '.html', locals())

@login_required()
def collaborators(request, event, user):
    """
    Event Collaborators Dashboard
    """
    if not Event.objects.filter(id = event).exists():
        raise Http404
    event = Event.objects.get(id = event)
    if not Organizer.objects.filter(event = event, profile__managers = user, is_creator = True).exists():
        return redirect('index')
    organizers = Organizer.objects.filter(event = event, is_creator = False)
    for organizer in organizers:
        organizer.invites = Invite.objects.filter(event = event, profile = organizer.profile, is_sent = True)
        organizer.invite_count = 0
        for invite in organizer.invites:
            organizer.invite_count += invite.recipients
    pendingRequests = Collaboration_request.objects.filter(event = event, accepted__isnull = True, is_rejected = False)
    rejectedRequests = Collaboration_request.objects.filter(event = event, is_rejected = True)
    return render(request, 'event/collaborators.html', locals())

@login_required()
@validate('POST')
def collaborator_toggle(request, organizer, params, user):
    """
    Toggle whether an organizer is visible or not
    """
    if not Organizer.objects.filter(id = organizer).exists():
        response = {
            'status':'FAIL',
            'error':'ORGANIZER_NOT_FOUND',
            'message':'The organizer doesn\'t exist.'
        }
        return json_response(response)
    organizer = Organizer.objects.get(id = organizer)
    if not Organizer.objects.filter(event = organizer.event, profile__managers = user, is_creator = True).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_AN_ORGANIZER',
            'message':'You don\'t have permission to edit this.'
        }
        return json_response(response)
    if organizer.is_public:
        organizer.is_public = False
    else:
        organizer.is_public = True
    organizer.save()
    response = {
        'status':'OK',
        'organizer': serialize_one(organizer)
    }
    return json_response(response)


@login_required()
@validate('GET')
def manage(request, id, params, user):
    if not Event.objects.filter(id = id).exists():
        raise Http404
    event = Event.objects.get(id = id)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        return redirect('index')
    isCreator = False
    if Organizer.objects.filter(event = event, profile__managers = user, is_creator = True).exists():
        isCreator = True
    pastEventList = {}
    profiles = Profile.objects.filter(managers = user)
    pids = []
    for profile in profiles:
        pids.append(profile.id)
    pastEvents = Event.objects.filter(Q(end_time = None, 
                                        start_time__lt = timezone.now()) | 
                                      Q(end_time__isnull = False, 
                                        end_time__lt = timezone.now()), 
                                      is_launched = True, 
                                      organizers__in = pids) \
                              .order_by('-start_time')
    eids = []
    for pastEvent in pastEvents:
            eids.append(pastEvent.id)
    purchases = Purchase.objects.filter(Q(checkout = None) | 
                                    Q(checkout__is_charged = True, 
                                      checkout__is_refunded = False), 
                                    event__in = eids, 
                                    is_expired = False)
    for purchase in purchases:
        if purchase.event.id in pastEventList:
            pastEventList[purchase.event.id]['quantity'] += 1
        else:
            pastEventList[purchase.event.id] = {
                'id': purchase.event.id,
                'name': purchase.event.name,
                'quantity': 1
            }
    purchase_items = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                        Q(purchase__checkout__is_charged = True, 
                                          purchase__checkout__is_refunded = False), 
                                        purchase__event = event, 
                                        purchase__is_expired = False).order_by('-id')
    purchases = {}
    for item in purchase_items:
        if item.purchase.id in purchases:
            if item.is_checked_in:
                purchases[item.purchase.id]['checked_in'] = True
            if item.ticket.id in purchases[item.purchase.id]['tickets']:
                purchases[item.purchase.id]['tickets'][item.ticket.id]['quantity'] += 1
            else:
                purchases[item.purchase.id]['tickets'].update({
                    item.ticket.id:{
                        'id':item.ticket.id,
                        'name':item.ticket.name,
                        'quantity':1
                    }
                })
        else:
            if item.purchase.amount > 0 and item.purchase.checkout.checkout_id.strip() != '':
                refundable = True
            else:
                refundable = False
            if item.is_checked_in:
                checkedIn = True
            else:
                checkedIn = False
            purchases[item.purchase.id] = {
                'id': item.id,
                'purchase_id': item.purchase.id,
                'refundable': refundable,
                'name': item.purchase.owner.first_name + ' ' + item.purchase.owner.last_name,
                'email': item.purchase.owner.email,
                'owner_id': item.purchase.owner.id,
                'code': item.purchase.code,
                'checked_in': checkedIn,
                'tickets': {
                    item.ticket.id:{
                        'id':item.ticket.id,
                        'name':item.ticket.name,
                        'quantity':1
                    }
                }
            }
            try:
                extra_fields = json.loads(item.ticket.extra_fields)
            except:
                extra_fields = {}
            finally:
                try:
                    item.extra_fields = item.extra_fields.replace("\'", "\"")
                    item.extra_fields = item.extra_fields.replace("u\"", "\"")
                    item.extra_fields = item.extra_fields.replace("\"d", "\'d")
                    item.extra_fields = item.extra_fields.replace("\"s", "\'s")
                    item_fields = json.loads(item.extra_fields)
                except:
                    item_fields = {}
                finally:
                    if type(item_fields) is dict:
                        purchases[item.purchase.id]['extra_fields'] = item_fields
                    else:
                        purchases[item.purchase.id]['extra_fields'] = {}
    tickets = Ticket.objects.filter(event=event, is_deleted=False)
    ticket_list = {}
    for item in purchase_items:
        if not item.ticket.id in ticket_list:
            ticket_list[item.ticket.id] = {
                'id': item.ticket.id,
                'name': item.ticket.name,
                'count': Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                        Q(purchase__checkout__is_charged = True, 
                                          purchase__checkout__is_refunded = False), 
                                        ticket = item.ticket, 
                                        purchase__is_expired = False).count()
            }
    checked_in = purchase_items.exclude(Q(checked_in_time = None)).count()
    purchases = OrderedDict(reversed(sorted(purchases.items())))
    rewards = Reward_item.objects.filter(owner = profiles[0], quantity__gt = 0, expiration_time__gte = timezone.now(), is_deleted = False)
    return render(request, 'event/manage.html', locals())

@login_required()
@validate('GET', ['id'])
def event(request, params, user):
    """
    Return serialized data for the event
    """
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@validate('GET', ['keyword'])
def search(request, params):
    """
    Search events by keyword
    """
    profiles = Profile.objects.filter(name__icontains = params['keyword'])
    pids = []
    for profile in profiles:
        pids.append(profile.id)
    events = Event.objects.filter(Q(end_time = None, start_time__gt = timezone.now()) | Q(end_time__isnull = False, end_time__gt = timezone.now()), Q(name__icontains = params['keyword']) | Q(organizers__in = pids), is_launched = True)
    results = []
    for event in events:
        eventObj = serialize_one(event)
        eventObj['event_url'] = layout.eventUrl(event)
        if event.organizers.all()[0].image:
            eventObj['image_url'] = event.organizers.all()[0].image.source.url
        else:
            eventObj['image_url'] = None
        results.append(eventObj)
    response = {
        'status':'OK',
        'events':results
    }
    return json_response(response)

@login_required()
@validate('GET', ['id'])
def graph_data(request, params, user):
    """
    Return data for the event's dashboard graph
    """
    if not Event.objects.filter(id = params['id']).exists():
        raise Http404
    event = Event.objects.get(id = params['id'])
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'events':'NOT_A_MANAGER'
        }
    else:
        purchases = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = event, 
                                        is_expired = False).annotate(rsvps=Count('items')).order_by('-created_time')
        
        purchase_data = {}
        for purchase in purchases:
            if purchase.created_time.strftime('%Y-%m-%d') in purchase_data:
                purchase_data[purchase.created_time.strftime('%Y-%m-%d')]['amount'] += purchase.amount
                purchase_data[purchase.created_time.strftime('%Y-%m-%d')]['rsvps'] += purchase.rsvps
            else:
                purchase_data[purchase.created_time.strftime('%Y-%m-%d')] = {
                    'amount': purchase.amount,
                    'rsvps': purchase.rsvps,
                    'date': purchase.created_time.strftime('%Y-%m-%d')
                }
        response = {
            'status':'OK',
            'purchases': purchase_data
        }
        return json_response(response)

@validate('POST', ['name', 'useremail', 'message', 'event'])
def issue(request, params):
    if not Event.objects.filter(id = params['event']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    if not REGEX_EMAIL.match(params['useremail']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    sendIssueEmail(params['name'], params['useremail'], params['message'], event)
    response = {
                'status':'OK'
    }
    return json_response(response)

# INVITES
@login_check()
def invite(request, event, user):
    if not Event.objects.filter(id = event, 
                                is_deleted = False).exists():
        raise Http404
    event = Event.objects.get(id = event)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        return redirect('index')
    profile = Organizer.objects.filter(event = event, profile__managers = user)[0].profile
    client = Mandrill(MANDRILL_API_KEY)
    sentInvites = Invite.objects.filter(event = event, is_sent = True, profile__managers = user).order_by('-sent_at')
    for invt in sentInvites:
        opens = 0
        totalOpens = 0
        results = Invite_stat.objects.filter(invite = invt).order_by('-clicks', '-opens')
        for email in results:
            opens += email.opens
            if email.opens > 0:
                totalOpens += 1
        invt.opens = opens
        invt.total_opens = totalOpens
    draftInvites = Invite.objects.filter(event = event, profile__managers = user, is_sent = False, is_deleted = False).order_by('-created_time')
    numLists = List_item.objects.filter(_list__owner = profile, is_deleted = False).count()
    return render(request, 'event/invite-dashboard.html', locals())

@login_check()
def invite_details(request, invite, user):
    if not Invite.objects.filter(id = invite, profile__managers = user, is_sent = True, is_deleted = False).exists():
        return redirect('index')
    invt = Invite.objects.get(id = invite)
    totalOpens = 0
    totalClicks = 0
    totalRSVPs = len(Purchase.objects.filter(invite = invt))
    results = Invite_stat.objects.filter(invite = invt).order_by('-clicks', '-opens')
    for email in results:
        if email.opens > 0:
            totalOpens += 1
        if email.clicks > 0:
            totalClicks += 1
    if invt.recipients > 0:
        openPercent = str("%.1f" % (totalOpens*100.0 / invt.recipients)) + "%"
        clickPercent = str("%.1f" % (totalClicks*100.0 / invt.recipients)) + "%"
        rsvpPercent = str("%.1f" % (totalRSVPs*100.0 / invt.recipients)) + "%"
    else:
        openPercent = "0%"
        clickPercent = "0%"
        rsvpPercent = "0%"
    return render(request, 'event/invite-details.html', locals())

@login_check()
def create_invite(request, event, user):
    if not Event.objects.filter(id = event, is_deleted = False).exists():
        raise Http404
    event = Event.objects.get(id = event)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        return redirect('index')
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    lists = List.objects.filter(owner = profile, is_deleted = False)
    for lt in lists:
        list_items = List_item.objects.filter(_list = lt, is_deleted = False)
        lt.items = list_items.count()
    previousInvites = Invite.objects.filter(event = event)
    activeButtonType = 'event'
    return render(request, 'event/invite.html', locals())

@login_check()
def edit_invite(request, invite, user):
    if not Invite.objects.filter(id = invite, profile__managers = user, is_deleted = False, is_sent = False).exists():
        return redirect('index')
    invite = Invite.objects.get(id = invite)
    event = invite.event
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    lists = List.objects.filter(owner = profile, is_deleted = False)
    for lt in lists:
        list_items = List_item.objects.filter(_list = lt, is_deleted = False)
        lt.items = list_items.count()
        lt.selected = False
        if invite.lists.filter(id = lt.id).exists():
            lt.selected = True
    if invite.button_target is None:
        activeButtonType = 'none'
    elif (invite.button_target) == 'http://bazaarboy.com' + layout.eventUrl(invite.event) + '?iid=' + str(invite.id):
        activeButtonType = 'event'
    else:
        activeButtonType = 'link'
    return render(request, 'event/invite.html', locals())

@login_check()
@validate('POST', [])
def copy_invite(request, params, invite, user):
    if not Invite.objects.filter(id = invite, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'INVITE_NOT_FOUND',
            'message':'The invite doesn\'t exist.'
        }
        return json_response(response)
    invite = Invite.objects.get(id = invite)
    new_invite = Invite(profile = invite.profile, event = invite.event, color = invite.color)
    if invite.image is not None:
        new_invite.image = invite.image
    if invite.message is not None:
        new_invite.message = invite.message
    if invite.details is not None:
        new_invite.details = invite.details
    if invite.heading is not None:
        new_invite.heading = invite.heading
    if invite.button_text is not None:
        new_invite.button_text = invite.button_text
    if invite.button_target is not None:
        new_invite.button_target = invite.button_target
    if invite.subject is not None:
        new_invite.subject = invite.subject
    new_invite.save()
    response = {
        'status':'OK',
        'invite':serialize_one(new_invite)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id', 'lists', 'message', 'button_type'], ['details', 'image', 'color', 'force', 'button_text', 'button_target', 'subject', 'heading'])
def new_invite(request, params, user):
    event = params['id']
    if not Event.objects.filter(id = event, is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = event)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_OWNER',
            'message':'This is not your event.'
        }
        return json_response(response)
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    if params['force'] != 'true' or params['lists'].strip() != '':
        if List.objects.filter(id__in = [x.strip() for x in params['lists'].split(',')], owner__managers = user).exists():
            lists = List.objects.filter(id__in = [x.strip() for x in params['lists'].split(',')], owner__managers = user, is_deleted = False)
        else:
            response = {
                'status':'FAIL',
                'error':'NO_VALID_LISTS',
                'message':'No Valid Lists Were Selected.'
            }
            return json_response(response)
    else:
        lists = []
    invite = Invite(event = event, profile = profile, message = params['message'])
    if params['details']:
        invite.details = params['details']
    if params['image'] and params['image'] != '':
        if Image.objects.filter(id = params['image']).exists():
            invite.image = Image.objects.get(id = params['image'])
    if params['color'] and params['color'] != '':
        invite.color = params['color']
    if params['button_text'] and  params['button_text'] != '':
        invite.button_text = params['button_text']
    if params['subject'] and  params['subject'] != '':
        invite.subject = params['subject']
    if params['heading'] and  params['heading'] != '':
        invite.heading = params['heading']
    invite.save()
    custom_link = 'http://bazaarboy.com' + layout.eventUrl(invite.event) + '?iid=' + str(invite.id)
    if params['button_type'] == 'link' and params['button_target']:
        custom_link = params['button_target']
    if params['button_type'] == 'none':
        custom_link = None
    invite.button_target = custom_link
    for lt in lists:
        invite.lists.add(lt)
    invite.save()
    response = {
        'status':'OK',
        'invite':serialize_one(invite)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id', 'lists', 'message', 'button_type'], ['details', 'image', 'color', 'deleteImg', 'force', 'button_text', 'button_target', 'subject', 'heading'])
def save_invite(request, params, user):
    invite = params['id']
    if not Invite.objects.filter(id = invite, profile__managers = user, is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'Invite_NOT_FOUND',
            'message':'The invite doesn\'t exist.'
        }
        return json_response(response)
    invite = Invite.objects.get(id = invite)
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    if params['force'] != 'true' or params['lists'].strip() != '':
        if List.objects.filter(id__in = [x.strip() for x in params['lists'].split(',')], owner__managers = user).exists():
            lists = List.objects.filter(id__in = [x.strip() for x in params['lists'].split(',')], owner__managers = user)
        else:
            response = {
                'status':'FAIL',
                'error':'NO_VALID_LISTS',
                'message':'No Valid Lists Were Selected.'
            }
            return json_response(response)
    else:
        lists = []
    invite.message = params['message']
    if params['details']:
        invite.details = params['details']
    if params['image'] and params['image'] != '':
        if Image.objects.filter(id = params['image']).exists():
            invite.image = Image.objects.get(id = params['image'])
    if params['color'] and params['color'] != '':
        invite.color = params['color']
    invite.lists.clear()
    for lt in lists:
        invite.lists.add(lt)
    if params['deleteImg'] and params['deleteImg'] == 'true':
        invite.image = None
    if params['button_text'] and params['button_text'] != '':
        invite.button_text = params['button_text']
    else:
        invite.button_text = None
    if params['subject'] and params['subject'] != '':
        invite.subject = params['subject']
    else:
        invite.subject = None
    if params['heading'] and  params['heading'] != '':
        invite.heading = params['heading']
    custom_link = 'http://bazaarboy.com' + layout.eventUrl(invite.event) + '?iid=' + str(invite.id)
    if params['button_type'] == 'link' and params['button_target']:
        custom_link = params['button_target']
    if params['button_type'] == 'none':
        custom_link = None
    invite.button_target = custom_link
    invite.save()
    response = {
        'status':'OK',
        'invite':serialize_one(invite)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id'])
def delete_invite(request, params, user):
    invite = params['id']
    if not Invite.objects.filter(id = invite, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'Invite_NOT_FOUND',
            'message':'The invite doesn\'t exist.'
        }
        return json_response(response)
    invite = Invite.objects.get(id = invite)
    invite.is_deleted = True
    invite.save()
    response = {
        'status': 'OK',
        'invite': serialize_one(invite)
    }
    return json_response(response)

@login_check()
def preview_invite(request, invite, user):
    if not Invite.objects.filter(id = invite, profile__managers = user, is_deleted = False, is_sent = False).exists():
        return redirect('index')
    invite = Invite.objects.get(id = invite)
    recipients = []
    sent = 0
    duplicates = 0
    unsubscribes = 0
    invitedList = []
    for lt in invite.lists.all():
        list_items = List_item.objects.filter(_list = lt, is_deleted = False)
        for item in list_items:
            if not Unsubscribe.objects.filter(Q(email = item.email), Q(profile = invite.profile) | Q(profile__isnull = True)).exists():
                if item.email.lower() not in recipients:
                    sent += 1
                    recipients.append(item.email.lower())
                else:
                    duplicates += 1
            else:
                unsubscribes += 1
    cost = INVITE_COST(sent) / 100
    return render(request, 'event/invite-preview.html', locals())

@login_check()
def preview_invite_template(request, invite, user):
    if not Invite.objects.filter(id = invite, profile__managers = user).exists():
        return redirect('index:index')
    invite = Invite.objects.get(id = invite)
    return render(request, 'event/invite-preview-template.html', locals())

@login_check()
@validate('POST', ['id'])
def send_invite(request, params, user):
    invite = params['id']
    if not Invite.objects.filter(id = invite, profile__managers = user, is_deleted = False, is_sent = False).exists():
        response = {
            'status':'FAIL',
            'error':'Invite_NOT_FOUND',
            'message':'The invite doesn\'t exist.'
        }
        return json_response(response)
    invite = Invite.objects.get(id = invite)
    recipients = []
    sent = 0
    duplicates = 0
    unsubscribes = 0
    invitedList = []
    client = Mandrill(MANDRILL_API_KEY)
    results = Invite_stat.objects.filter(event = invite.event)
    for lt in invite.lists.all():
        list_items = List_item.objects.filter(_list = lt, is_deleted = False)
        for item in list_items:
            if not Unsubscribe.objects.filter(Q(email = item.email), Q(profile = invite.profile) | Q(profile__isnull = True)).exists():
                if item.email.lower() not in recipients:
                    sent += 1
                    recipients.append(item.email.lower())
                else:
                    duplicates += 1
            else:
                unsubscribes += 1
    if sent == 0:
        response = {
            'status': 'FAIL',
            'error': 'NO_RECIPIENTS',
            'message': 'The message will not have any recipients, please use another list.'
        }
        return json_response(response)
    if invite.paid == True or INVITE_COST(sent) == 0:
        sendEventInvite(invite, recipients)
    else:
        response = {
            'status':'PAYMENT',
            'cost':INVITE_COST(sent),
            'sent':sent,
            'publishable_key':STRIPE_PUBLISHABLE_KEY,
            'invite':serialize_one(invite)
        }
        return json_response(response)
    response = {
        'status':'OK',
        'sent': sent,
        'duplicates': duplicates,
        'unsubscribes': unsubscribes,
        'invite': serialize_one(invite)
    }
    return json_response(response)


@login_check()
@validate('POST', [], ['subject', 'events', 'emails', 'message', 'inviter'])
def manual_invite(request, id, params, user):
    if not Event.objects.filter(id = id, 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = id)
    if not params['events'] and not params['emails']:
        response = {
            'status':'FAIL',
            'error':'NO_EMAILS',
            'message':'You need to send at least one email.'
        }
        return json_response(response)
    emails = []
    if not params['inviter']:
        profiles = Profile.objects.filter(managers = user)
        inviter = profiles.all()[0].name
        pids = []
        for profile in profiles:
            pids.append(profile.id)
        if params['events']:
            eids = params['events'].replace(" ", "").split(",")
            for event_id in eids:
                if not Organizer.objects.filter(event = event_id, 
                                        profile__managers = user).exists():
                    response = {
                        'status':'FAIL',
                        'events':'NOT_AN_ORGANIZER',
                        'message': 'You were not an organizer on at least one of the chosen events'
                    }
                    return json_response(response)
            purchases = Purchase.objects.filter(Q(checkout = None) | 
                                            Q(checkout__is_charged = True, 
                                              checkout__is_refunded = False), 
                                            event__in = eids,
                                            event__organizers__in = pids, 
                                            is_expired = False)
            for purchase in purchases.all():
                if not any(purchase.owner.email.lower() == val.lower() for val in emails):
                    emails.append(purchase.owner.email)
    else:
        inviter = params['inviter']
    if params['emails']:
        additional_emails = params['emails'].replace(" ", "").split(",")
        for email in additional_emails:
            if not any(email.lower() == val.lower() for val in emails) and REGEX_EMAIL.match(email):
                emails.append(email)
    if params['subject']:
        subject = params['subject']
    else:
        subject = ''
    if params['message']:
        message = params['message']
    else:
        message = ''
    for email in emails:
        if not Unsubscribe.objects.filter(email = email).exists():
            sendManualEventInvite(event, email, subject, inviter, message)
    response = {
        'status':'OK',
        'count': str(len(emails))
    }
    return json_response(response)

# FOLLOW UPS
@login_check()
def follow_up(request, event, user):
    """
    Follow Ups sent/drafts page for event
    """
    if not Organizer.objects.filter(event__id = event, profile__managers = user, is_creator = True).exists():
        raise Http404
    event = Event.objects.get(id = event)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        return redirect('index')
    organizer = Organizer.objects.filter(event = event, profile__managers = user)[0]
    if Recap.objects.filter(organizer = organizer, is_viewed = False).exists():
        recap = Recap.objects.get(organizer = organizer)
        recap.is_viewed = True
        recap.save()
    sentFollowUps = Follow_up.objects.filter(recap__organizer__event = event, is_sent = True, recap__organizer__profile__managers = user).order_by('-sent_at')
    draftFollowUps = Follow_up.objects.filter(recap__organizer__event = event, is_sent = False, recap__organizer__profile__managers = user, is_deleted = False).order_by('-created_time')
    return render(request, 'event/follow-up-dashboard.html', locals())

@login_check()
def follow_up_details(request, follow_up, user):
    if not Follow_up.objects.filter(id = follow_up, recap__organizer__profile__managers = user, is_deleted = False, is_sent = True).exists():
        return redirect('index')
    follow_up = Follow_up.objects.get(id = follow_up)
    totalOpens = 0
    totalClicks = 0
    results = Follow_up_stat.objects.filter(follow_up = follow_up).order_by('-clicks', '-opens')
    for email in results:
        if email.opens > 0:
            totalOpens += 1
        if email.clicks > 0:
            totalClicks += 1
    openPercent = str("%.1f" % (totalOpens*100.0 / follow_up.recipients)) + "%"
    clickPercent = str("%.1f" % (totalClicks*100.0 / follow_up.recipients)) + "%"
    return render(request, 'event/follow-up-details.html', locals())

@login_check()
def create_follow_up(request, event, user):
    if not Organizer.objects.filter(event__id = event, event__is_deleted = False, profile__managers = user, is_creator = True).exists():
        raise Http404
    event = Event.objects.get(id = event)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        return redirect('index')
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    sent_tickets = []
    for fu in Follow_up.objects.filter(recap__organizer__event = event, is_sent = True):
        for ticket in fu.tickets.all():
            sent_tickets.append(ticket.id)
    tickets = Ticket.objects.filter(event = event).exclude(id__in = sent_tickets)
    for ticket in tickets:
        ticket.items = Purchase_item.objects.filter(ticket = ticket).values_list('purchase__id', flat=True).distinct().count()
    previousFollowUps = Follow_up.objects.filter(recap__organizer__event = event)
    activeButtonType = 'event'
    rewards = Reward.objects.filter(creator = profile, is_deleted = False)
    return render(request, 'event/follow-up.html', locals())

@login_check()
def edit_follow_up(request, follow_up, user):
    if not Follow_up.objects.filter(id = follow_up, recap__organizer__profile__managers = user, is_deleted = False, is_sent = False).exists():
        return redirect('index')
    follow_up = Follow_up.objects.get(id = follow_up)
    event = follow_up.recap.organizer.event
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    sent_tickets = []
    for fu in Follow_up.objects.filter(recap__organizer__event = event, is_sent = True):
        for ticket in fu.tickets.all():
            sent_tickets.append(ticket.id)
    tickets = Ticket.objects.filter(event = event).exclude(id__in = sent_tickets)
    for ticket in tickets:
        ticket.items = Purchase_item.objects.filter(ticket = ticket).values_list('purchase__id', flat=True).distinct().count()
        ticket.selected = False
        if follow_up.tickets.filter(id = ticket.id).exists():
            ticket.selected = True
    activeButtonType = 'link'
    if follow_up.attachment:
        if follow_up.attachment.source.url.split("?", 1)[0] == str(follow_up.button_target).split("?", 1)[0]:
            activeButtonType = 'attachment'
    if (follow_up.button_target) == 'http://bazaarboy.com' + layout.eventUrl(follow_up.recap.organizer.event):
        activeButtonType = 'event'
    if follow_up.reward_item is not None:
        activeButtonType = 'gift'
    rewards = Reward.objects.filter(creator = profile, is_deleted = False)
    return render(request, 'event/follow-up.html', locals())

@login_check()
@validate('POST', ['id', 'tickets', 'message', 'heading', 'button_text', 'button_type'], ['image', 'pdf', 'color', 'custom_link', 'gift_id', 'gift_expiration'])
def new_follow_up(request, params, user):
    profiles = Profile.objects.filter(managers = user)
    pids = []
    for profile in profiles:
        pids.append(profile.id)
    if not Organizer.objects.filter(event__id = params['id'], profile__in = pids).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_OWNER',
            'message':'This is not your event.'
        }
        return json_response(response)
    current_organizer = Organizer.objects.get(event__id = params['id'], profile__in = pids)
    if not Recap.objects.filter(organizer = current_organizer).exists():
        recap = Recap(organizer = current_organizer)
        recap.save()
    else:
        recap = Recap.objects.get(organizer = current_organizer)
    if Ticket.objects.filter(id__in = [x.strip() for x in params['tickets'].split(',')], event__organizers__managers = user).exists():
        tickets = Ticket.objects.filter(id__in = [x.strip() for x in params['tickets'].split(',')], event__organizers__managers = user)
    else:
        response = {
            'status':'FAIL',
            'error':'NO_VALID_LISTS',
            'message':'No Valid Lists Were Selected.'
        }
        return json_response(response)
    follow_up = Follow_up(recap = recap, message = params['message'], heading = params['heading'], button_text = params['button_text'])
    if params['image'] and params['image'] != '':
        if Image.objects.filter(id = params['image']).exists():
            follow_up.image = Image.objects.get(id = params['image'])
    if params['pdf'] and params['pdf'] != '':
        if Pdf.objects.filter(id = params['pdf']).exists():
            follow_up.attachment = Pdf.objects.get(id = params['pdf'])
    if params['color'] and params['color'] != '':
        follow_up.color = params['color']
    custom_link = 'http://bazaarboy.com' + layout.eventUrl(recap.organizer.event)
    if params['button_type'] == 'attachment' and follow_up.attachment:
        custom_link = follow_up.attachment.source.url
    if params['button_type'] == 'link' and params['custom_link']:
        custom_link = params['custom_link']
    follow_up.button_target = custom_link
    follow_up.save()
    for ticket in tickets:
        follow_up.tickets.add(ticket)
    if params['gift_id'] and params['gift_expiration']:
        if not Reward.objects.filter(id = params['gift_id'], creator = follow_up.recap.organizer.profile, is_deleted = False).exists():
            response = {
                'status':'FAIL',
                'error':'INVALID_GIFT',
                'message':'The gift you chose is invalid'
            }
            return json_response(response)
        reward = Reward.objects.get(id = params['gift_id'])
        exp_time = timezone.make_aware(parser.parse(params['gift_expiration']), timezone.get_current_timezone())
        if exp_time < timezone.now():
            response = {
                'status':'FAIL',
                'error':'INVALID_GIFT_EXPIRATION',
                'message':'The gift must expire after today'
            }
            return json_response(response)
        reward_item = Reward_item(reward = reward, owner = follow_up.recap.organizer.profile, quantity = 0, received = 0, expiration_time = params['gift_expiration'])
        reward_item.save()
        follow_up.reward_item = reward_item
    follow_up.save()
    response = {
        'status':'OK',
        'follow_up':serialize_one(follow_up)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id', 'tickets', 'message', 'heading', 'button_text', 'button_type'], ['image', 'pdf', 'color', 'deleteImg', 'deletePdf', 'custom_link', 'gift_id', 'gift_expiration'])
def save_follow_up(request, params, user):
    if not Follow_up.objects.filter(id = params['id'], recap__organizer__profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NO_FOLLOW_UP',
            'message':'No follow up exists.'
        }
        return json_response(response)
    follow_up = Follow_up.objects.get(id = params['id'])
    if Ticket.objects.filter(id__in = [x.strip() for x in params['tickets'].split(',')], event__organizer__profile__managers = user).exists():
        tickets = Ticket.objects.filter(id__in = [x.strip() for x in params['tickets'].split(',')], event__organizer__profile__managers = user)
    else:
        response = {
            'status':'FAIL',
            'error':'NO_VALID_LISTS',
            'message':'No Valid Lists Were Selected.'
        }
        return json_response(response)
    follow_up.message = params['message']
    follow_up.heading = params['heading']
    follow_up.button_text = params['button_text']
    if params['image'] and params['image'] != '':
        if Image.objects.filter(id = params['image']).exists():
            follow_up.image = Image.objects.get(id = params['image'])
    if params['pdf'] and params['pdf'] != '':
        if Pdf.objects.filter(id = params['pdf']).exists():
            follow_up.attachment = Pdf.objects.get(id = params['pdf'])
    if params['color'] and params['color'] != '':
        follow_up.color = params['color']
    follow_up.tickets.clear()
    for ticket in tickets:
        follow_up.tickets.add(ticket)
    if params['deleteImg'] and params['deleteImg'] == 'true':
        follow_up.image = None
    if params['deletePdf'] and params['deletePdf'] == 'true':
        follow_up.attachment = None
    custom_link = 'http://bazaarboy.com' + layout.eventUrl(follow_up.recap.organizer.event)
    if params['button_type'] == 'attachment' and follow_up.attachment:
        custom_link = follow_up.attachment.source.url
    if params['button_type'] == 'link' and params['custom_link']:
        custom_link = params['custom_link']
    if params['gift_id'] and params['gift_expiration']:
        if not Reward.objects.filter(id = params['gift_id'], creator = follow_up.recap.organizer.profile, is_deleted = False).exists():
            response = {
                'status':'FAIL',
                'error':'INVALID_GIFT',
                'message':'The gift you chose is invalid'
            }
            return json_response(response)
        reward = Reward.objects.get(id = params['gift_id'])
        exp_time = timezone.make_aware(parser.parse(params['gift_expiration']), timezone.get_current_timezone())
        if exp_time < timezone.now():
            response = {
                'status':'FAIL',
                'error':'INVALID_GIFT_EXPIRATION',
                'message':'The gift must expire after today'
            }
            return json_response(response)
        reward_item = Reward_item(reward = reward, owner = follow_up.recap.organizer.profile, quantity = 0, received = 0, expiration_time = params['gift_expiration'])
        reward_item.save()
        follow_up.reward_item = reward_item
    else:
        follow_up.reward_item = None
    follow_up.button_target = custom_link
    follow_up.save()
    response = {
        'status':'OK',
        'follow_up':serialize_one(follow_up)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id'])
def delete_follow_up(request, params, user):
    follow_up = params['id']
    if not Follow_up.objects.filter(id = follow_up, recap__organizer__profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'FOLLOW_UP_NOT_FOUND',
            'message':'The follow up doesn\'t exist.'
        }
        return json_response(response)
    follow_up = Follow_up.objects.get(id = follow_up)
    follow_up.is_deleted = True
    follow_up.save()
    response = {
        'status': 'OK',
        'invite': serialize_one(follow_up)
    }
    return json_response(response)

@login_check()
def preview_follow_up(request, follow_up, user):
    if not Follow_up.objects.filter(id = follow_up, recap__organizer__profile__managers = user, is_deleted = False, is_sent = False).exists():
        return redirect('index')
    follow_up = Follow_up.objects.get(id = follow_up)
    recipients = []
    sent = 0
    duplicates = 0
    unsubscribes = 0
    alreadyEmailed = 0
    emailedList = []
    results = Follow_up_stat.objects.filter(event = follow_up.recap.organizer.event)
    for result in results:
        emailedList.append(result.to.lower())
    for ticket in follow_up.tickets.all():
        list_items = Purchase_item.objects.filter(ticket = ticket)
        for item in list_items:
            if not Unsubscribe.objects.filter(Q(email = item.purchase.owner.email), Q(profile = follow_up.recap.organizer.profile) | Q(profile__isnull = True)).exists():
                if item.purchase.owner.email.lower() not in recipients:
                    if item.purchase.owner.email.lower() not in emailedList:
                        recipients.append(item.purchase.owner.email.lower())
                        sent += 1
                    else:
                        alreadyEmailed += 1
                else:
                    duplicates += 1
            else:
                unsubscribes += 1
    cost = FOLLOW_UP_COST(sent) / 100
    publishable_key = STRIPE_PUBLISHABLE_KEY
    return render(request, 'event/follow-up-preview.html', locals())

@login_check()
def preview_follow_up_template(request, follow_up, user):
    if not Follow_up.objects.filter(id = follow_up, recap__organizer__profile__managers = user).exists():
        return redirect('index')
    follow_up = Follow_up.objects.get(id = follow_up)
    return render(request, 'event/follow-up-preview-template.html', locals())

@login_check()
@validate('POST', ['id'])
def send_follow_up(request, params, user):
    if not Follow_up.objects.filter(id = params['id'], recap__organizer__profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'FOLLOW_UP_NOT_FOUND',
            'message':'The follow up doesn\'t exist.'
        }
        return json_response(response)
    follow_up = Follow_up.objects.get(id = params['id'])
    recipients = []
    sent = 0
    duplicates = 0
    unsubscribes = 0
    alreadyEmailed = 0
    emailedList = []
    results = Follow_up_stat.objects.filter(event = follow_up.recap.organizer.event)
    for result in results:
        emailedList.append(result.to.lower())
    for ticket in follow_up.tickets.all():
        list_items = Purchase_item.objects.filter(ticket = ticket)
        for item in list_items:
            if not Unsubscribe.objects.filter(Q(email = item.purchase.owner.email), Q(profile = follow_up.recap.organizer.profile) | Q(profile__isnull = True)).exists():
                if item.purchase.owner.email.lower() not in recipients:
                    if item.purchase.owner.email.lower() not in emailedList:
                        recipients.append(item.purchase.owner.email.lower())
                        sent += 1
                    else:
                        alreadyEmailed += 1
                else:
                    duplicates += 1
            else:
                unsubscribes += 1
    cost = FOLLOW_UP_COST(sent) / 100
    if sent == 0:
        response = {
            'status': 'FAIL',
            'error': 'NO_RECIPIENTS',
            'message': 'The message will not have any recipients, please use another ticket.'
        }
        return json_response(response)
    if follow_up.paid == True or FOLLOW_UP_COST(sent) == 0:
        if follow_up.reward_item is not None:
            follow_up.reward_item.received = len(recipients)
            follow_up.reward_item.save()
        sendFollowUp(follow_up, recipients)
    else:
        response = {
            'status':'PAYMENT',
            'cost':FOLLOW_UP_COST(sent),
            'sent':sent,
            'publishable_key':STRIPE_PUBLISHABLE_KEY,
            'follow_up':serialize_one(follow_up),
            'event':serialize_one(follow_up.recap.organizer.event)
        }
        return json_response(response)
    response = {
        'status':'OK',
        'sent': sent,
        'duplicates': duplicates,
        'unsubscribes': unsubscribes,
        'already_invited': alreadyEmailed,
        'follow_up': serialize_one(follow_up)
    }
    return json_response(response)

@login_check()
@validate('POST', ['name'])
def follow_up_attachment(request, user, params):
    """
    Create Attachment For Follow Up
    """
    if not request.FILES.has_key('attachment_file'):
        response = {
            'status': 'FAIL',
            'error': 'NO_FILE',
            'message': 'Upload failed. Try again.'
        }
        return json_response(response)
    else:
        # Validate the MIME type of the file
        attachment = request.FILES['attachment_file']
        newPdf = Pdf(source = attachment, name = params['name'])
        newPdf.save()
        response = {
            'status': 'OK',
            'pdf': serialize_one(newPdf),
            'url': newPdf.source.url
        }
        return json_response(response)

@login_required()
@validate('POST', ['profile'])
def create(request, params, user):
    """
    Create a new event
    """
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the profile.'
        }
        return json_response(response)
    # Create event
    event = Event(start_time = timezone.now() + timedelta(days = 7))
    if profile.color:
        event.color = profile.color
    event.save()
    # Set the profile as the organizer and creator of the event
    organizer = Organizer(event = event, profile = profile, is_creator = True)
    organizer.save()
    recap = Recap(organizer = organizer)
    recap.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_required()
@validate('POST', 
          ['id'], 
          ['name', 'summary', 'description', 'cover', 'caption', 'tags', 
           'category', 'start_time', 'end_time', 'location', 'latitude', 
           'longitude', 'slug', 'color'])
def edit(request, params, user):
    """
    Edit an existing event
    """
    # Check if the event is valid
    reschedule_email = False
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Go through all the params and edit the event accordingly
    if params['name'] is not None:
        params['name'] = cgi.escape(params['name'])
        if not (0 < len(params['name']) <= 150):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Event name cannot be blank or over 150 characters.'
            }
            return json_response(response)
        else:
            if not event.name == params['name']:
                reschedule_email = True
            event.name = params['name']
    if params['summary'] is not None:
        params['summary'] = cgi.escape(params['summary'])
        if len(params['summary']) > 250:
            response = {
                'status':'FAIL',
                'error':'SUMMARY_TOO_LONG',
                'message':'The summary must be within 250 characters.'
            }
            return json_response(response)
        else:
            event.summary = params['summary']
    if params['description'] is not None:
        params['description'] = sanitize_redactor_input(params['description'])
        if len(params['description']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_DESCRIPTION',
                'message':'Description cannot be blank.'
            }
            return json_response(response)
        else:
            event.description = params['description']
    if params['cover'] is not None:
        if params['cover'].lower() == 'delete':
            if event.cover is not None:
                oldCover = Image.objects.get(id = event.cover.id)
                oldCover.delete()
                event.cover = None
        elif not Image.objects.filter(id = params['cover']).exists():
            response = {
                'status':'FAIL',
                'error':'COVER_IMAGE_NOT_FOUND',
                'message':'The cover image doesn\'t exist.'
            }
            return json_response(response)
        else:
            cover = Image.objects.get(id = params['cover'])
            if event.cover is not None:
                oldCover = Image.objects.get(id = event.cover.id)
                oldCover.delete()
            cover.is_archived = True
            cover.save()
            event.cover = cover
    if params['color'] is not None and len(params['color']) == 7:
        event.color = params['color']
    if params['caption'] is not None:
        params['caption'] = cgi.escape(params['caption'])
        if event.cover is None:
            response = {
                'status':'FAIL',
                'error':'NO_COVER',
                'message':'You must set a cover image before adding caption.'
            }
            return json_response(response)
        elif len(params['caption']) > 100:
            response = {
                'status':'FAIL',
                'error':'CAPTION_TOO_LONG',
                'message':'The caption must be within 100 characters.'
            }
            return json_response(response)
        else:
            event.cover.caption = params['caption']
            event.cover.save()
    if params['tags'] is not None:
        params['tags'] = cgi.escape(params['tags'])
        if len(params['tags']) > 50:
            response = {
                'status':'FAIL',
                'error':'TAGS_TOO_LONG',
                'message':'The tags must be within 150 characters.'
            }
            return json_response(response)
        else:
            event.tags = params['tags']
    if params['start_time'] is not None:
        if not event.start_time == params['start_time'] and event.end_time is None:
            reschedule_email = True
        event.start_time = params['start_time']
    if params['end_time'] is not None:
        if params['end_time'] == 'none':
            event.end_time = None
        else:
            if not event.end_time == params['end_time']:
                reschedule_email = True
            event.end_time = params['end_time']
    if event.end_time is not None:
        if event.start_time is not None and event.start_time > event.end_time:
            response = {
                'status':'FAIL',
                'error':'INVALID_TIMING',
                'message':'End time cannot be before start time.'
            }
            return json_response(response)
    if params['location'] is not None:
        params['location'] = cgi.escape(params['location'])
        if len(params['location']) > 100:
            response = {
                'status':'FAIL',
                'error':'LOCATION_TOO_LONG',
                'message':'The location must be within 100 characters.'
            }
            return json_response(response)
        else:
            event.location = params['location']
    if params['latitude'] is not None and params['longitude'] is not None: 
        if (params['latitude'].lower() == 'none' or 
            params['longitude'].lower() == 'none'):
            event.latitude = None
            event.longitude = None
        elif not (-90.0 <= float(params['latitude']) <= 90.0 and 
                -180.0 <= float(params['longitude']) <= 180.0):
            response = {
                'status':'FAIL',
                'error':'INVALID_COORDINATES',
                'message':'Latitude/longitude combination is invalid.'
            }
            return json_response(response)
        else:
            event.latitude = float(params['latitude'])
            event.longitude = float(params['longitude'])
    if params['category'] is not None:
        params['category'] = cgi.escape(params['category'])
        if len(params['category']) > 30:
            response = {
                'status':'FAIL',
                'error':'INVALID_CATEGORY',
                'message':'Category cannot be over 30 characters.'
            }
            return json_response(response)
        else:
            event.category = params['category']
    if params['slug'] is not None:
        params['slug'] = cgi.escape(params['slug'])
        if params['slug'] == 'none':
            event.slug = None
        elif not REGEX_SLUG.match(params['slug']):
            response = {
                'status':'FAIL',
                'error':'INVALID_SLUG',
                'message':'The URL shortcut must be a combination of alphanumeric characters and hyphens.'
            }
            return json_response(response)
        elif Event.objects.filter(slug = params['slug'], is_deleted = False) \
                          .exclude(id = event.id).exists():
            response = {
                'status':'FAIL',
                'error':'DUPLICATE_SLUG',
                'message':'The URL shortcut has already been taken.'
            }
            return json_response(response)
        else:
            event.slug = params['slug']
    # Save the changes
    event.save()
    if reschedule_email and Recap.objects.filter(organizer__event = event).exists() and event.is_launched:
        recaps = Recap.objects.filter(organizer__event = event)
        client = Mandrill(MANDRILL_API_KEY)
        for recap in recaps:
            try:
                if recap.email_id is not None:
                    mail_cancel = client.messages.cancel_scheduled(id = recap.email_id)
                    recap.email_id = None
            except Exception, e:
                logging.error(str(e))
            if event.start_time >= timezone.now():
                mail_send = sendRecapReminder(recap.organizer)
                recap.email_id = mail_send[0]['_id']
            recap.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@validate('GET', ['hashtag'], ['event_id'])
def instagram_photos(request, params):
    tenMinutesAgo = timezone.now() - timedelta(minutes = 10)
    update_feed = True
    if Instagram_feed.objects.filter(hashtag = params['hashtag'].lower()).exists():
        feed = Instagram_feed.objects.filter(hashtag = params['hashtag'].lower())[0]
        if feed.updated_time > tenMinutesAgo:
            images = json.loads(feed.images)
            update_feed = False
        else:
            update_feed = True
    if update_feed is True:
        api = InstagramAPI(client_id=INSTAGRAM_CLIENT_ID, client_secret=INSTAGRAM_SECRET)
        instagram_photos = api.tag_recent_media(count=30, tag_name=params['hashtag'])
        images = []
        for photo in instagram_photos[0]:
            images.append({'high_res':photo.images['standard_resolution'].url, 'thumb':photo.images['thumbnail'].url})
        feed, created = Instagram_feed.objects.get_or_create(hashtag = params['hashtag'].lower())
        feed.images = json.dumps(images)
        feed.updated_time = timezone.now()
        feed.save()
    if params['event_id'] is not None:
        if Event.objects.filter(id = params['event_id']).exists():
            event = Event.objects.get(id = params['event_id'])
            color = event.color
    return render_to_response('components/instagram.html', locals(), context_instance=RequestContext(request))

@login_required()
@validate('POST', ['id'], ['profile', 'email'])
def request_organizer(request, params, user):
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    organizer = Organizer.objects.filter(event = event, profile__managers = user)[0]
    if params['profile']:
        if not Profile.objects.filter(id = params['profile']).exists():
            response = {
                'status':'FAIL',
                'error':'PROFILE_NOT_FOUND',
                'message':'The profile doesn\'t exist.'
            }
            return json_response(response)
        profile = Profile.objects.get(id = params['profile'])
        if Organizer.objects.filter(event = event, profile = profile).exists():
            response = {
                'status':'FAIL',
                'error':'ALREADY_AN_ORGANIZER',
                'message':'The profile is already an organizer.'
            }
            return json_response(response)
        collaboration = Collaboration_request(event = event, sender = organizer, profile = profile)
        collaboration.save()
        if collaboration.profile.email:
            sendCollaborationRequest(collaboration)
        response = {
            'status':'OK',
            'collaboration':serialize_one(collaboration)
        }
        return json_response(response)
    elif params['profile'] is None and params['email']:
        if not REGEX_EMAIL.match(params['email']):
            response = {
                'status':'FAIL',
                'error':'BAD_EMAIL',
                'message':'Please enter a valid email address.'
            }
            return json_response(response)
        collaboration = Collaboration_request(event = event, sender = organizer, email = params['email'])
        collaboration.save()
        sendCollaborationRequest(collaboration)
        response = {
            'status':'OK',
            'collaboration':serialize_one(collaboration)
        }
        return json_response(response)
    else:
        response = {
            'status':'FAIL',
            'error':'ERROR',
            'message':'There was an error sending the request.'
        }
        return json_response(response)

@login_required()
@validate('POST', ['id'])
def accept_organizer_request(request, params, user):
    # Check if the request is valid
    if not Collaboration_request.objects.filter(id = params['id'], accepted__isnull = True, is_rejected = False).exists():
        response = {
            'status':'FAIL',
            'error':'REQUEST_NOT_FOUND',
            'message':'The request doesn\'t exist.'
        }
        return json_response(response)
    collaboration_request = Collaboration_request.objects.get(id = params['id'])
    if not Collaboration_request.objects.filter(event = collaboration_request.event, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the request.'
        }
        return json_response(response)
    if Organizer.objects.filter(event = collaboration_request.event, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'ALREADY_AN_ORGANIZER',
            'message':'The profile is already an organizer.'
        }
        return json_response(response)
    organizer = Organizer(event = collaboration_request.event, profile = collaboration_request.profile)
    organizer.save()
    collaboration_request.accepted = timezone.now()
    collaboration_request.save()
    sendCollaborationResponse(collaboration_request, True)
    recap = Recap(organizer = organizer)
    recap.save()
    if recap.organizer.event.is_launched and recap.organizer.event.start_time >= timezone.now():
        mail_send = sendRecapReminder(organizer)
        recap.email_id = mail_send[0]['_id']
        recap.save()
    response = {
        'status':'OK',
        'collaboration':serialize_one(collaboration_request),
        'organizer':serialize_one(organizer)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def reject_organizer_request(request, params, user):
    if not Collaboration_request.objects.filter(id = params['id'], accepted__isnull = True, is_rejected = False).exists():
        response = {
            'status':'FAIL',
            'error':'REQUEST_NOT_FOUND',
            'message':'The request doesn\'t exist.'
        }
        return json_response(response)
    collaboration_request = Collaboration_request.objects.get(id = params['id'])
    if not Collaboration_request.objects.filter(event = collaboration_request.event, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the request.'
        }
        return json_response(response)
    if Organizer.objects.filter(event = collaboration_request.event, profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'ALREADY_AN_ORGANIZER',
            'message':'The profile is already an organizer.'
        }
        return json_response(response)
    profile = Profile.objects.filter(managers = user)[0]
    collaboration_request.is_rejected = True
    collaboration_request.save()
    sendCollaborationResponse(collaboration_request, False)
    response = {
        'status':'OK',
        'collaboration':serialize_one(collaboration_request)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'profile'])
def add_organizer(request, params, user):
    if not request.session.has_key('admin'):
        # No admin session, block from login
        response = {
            'status':'FAIL',
            'message':'Not an Admin.'
        }
        return json_response(response)
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    user_profile = Organizer.objects.filter(event = event)[0].profile
    # Check if the profile exists
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    # Check if the profile is an organizer of the event
    if Organizer.objects.filter(event = event, profile = profile).exists():
        response = {
            'status':'FAIL',
            'error':'ALREADY_AN_ORGANIZER',
            'message':'The profile is already an organizer.'
        }
        return json_response(response)
    # Add the profile as an organizer
    organizer = Organizer(event = event, profile = profile)
    organizer.save()
    result_profile = serialize_one(profile)
    if profile.image:
        result_profile['image_url'] = profile.image.source.url
    else:
        result_profile['image_url'] = None
    if profile.email:
        sendOrganizerAddedEmail(event, user_profile, profile)
    recap = Recap(organizer = organizer)
    recap.save()
    if event.is_launched and event.start_time >= timezone.now():
        mail_send = sendRecapReminder(organizer)
        recap.email_id = mail_send[0]['_id']
        recap.save()
    response = {
        'status':'OK',
        'profile': result_profile
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'profile'])
def delete_organizer(request, params, user):
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if the profile exists
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    # Check if the profile is an organizer of the event
    if not Organizer.objects.filter(event = event, profile = profile).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_AN_ORGANIZER',
            'message':'The profile is not an organizer.'
        }
        return json_response(response)
    organizer = Organizer.objects.get(event = event, profile = profile)
    # Check if the profile is the creator of the event
    if organizer.is_creator:
        response = {
            'status':'FAIL',
            'error':'PROFILE_IS_CREATOR',
            'message':'You cannot remove the creator from organizers.'
        }
        return json_response(response)
    if Recap.objects.filter(organizer = organizer).exists():
        recap = Recap.objects.get(organizer = organizer)
        if recap.email_id is not None:
            client = Mandrill(MANDRILL_API_KEY)
            client.messages.cancel_scheduled(id = recap.email_id)
    # Remove the profile from organizers
    organizer.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def launch(request, params, user):
    """
    Launch an event
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if the event has been launched
    if event.is_launched:
        response = {
            'status':'FAIL',
            'error':'LAUNCHED_EVENT',
            'message':'The event has been launched.'
        }
        return json_response(response)
    # Check if the Event has Paid Tickets and the user has connected Stripe
    creator = Organizer.objects.get(event = event, 
                                    is_creator = True).profile
    paymentAccount = creator.payment_account
    tickets = Ticket.objects.filter(event = event)
    if paymentAccount is None:
        for ticket in tickets:
            if ticket.price > 0 and not ticket.is_deleted:
                response = {
                    'status':'FAIL',
                    'error':'NO_PAYMENT_ACCOUNT',
                    'message':'Must have a Stripe account before selling Priced Tickets'
                }
                return json_response(response)
    # Launch the event
    event.is_launched = True
    event.launched_time = timezone.now()
    event.save()
    organizers = Organizer.objects.filter(event = event)
    for organizer in organizers:
        if Recap.objects.filter(organizer = organizer).exists() and event.start_time >= timezone.now():
            recap = Recap.objects.get(organizer = organizer)
            if recap.organizer.profile.email:
                recap_email = sendRecapReminder(organizer)
                recap.email_id = recap_email[0]['_id']
            recap.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delaunch(request, params, user):
    """
    Take an event offline
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if the event is launched
    if not event.is_launched:
        response = {
            'status':'FAIL',
            'error':'NOT_LAUNCHED',
            'message':'The event is not yet launched.'
        }
        return json_response(response)
    # Mark the event as offline
    event.is_launched = False
    event.save()
    organizers = Organizer.objects.filter(event = event)
    for organizer in organizers:
        if Recap.objects.filter(organizer = organizer).exists():
            recap = Recap.objects.get(organizer = organizer)
            if recap.email_id is not None:
                client = Mandrill(MANDRILL_API_KEY)
                client.messages.cancel_scheduled(id = recap.email_id)
                recap.email_id = None
                recap.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete(request, params, user):
    """
    Delete an event
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Mark the tickets and the event as deleted
    Ticket.objects.filter(event = event).update(is_deleted = True)
    event.is_deleted = True
    event.save()
    organizers = Organizer.objects.filter(event = event)
    for organizer in organizers:
        if Recap.objects.filter(organizer = organizer).exists():
            recap = Recap.objects.get(organizer = organizer)
            if recap.email_id is not None:
                client = Mandrill(MANDRILL_API_KEY)
                client.messages.cancel_scheduled(id = recap.email_id)
    response = {
        'status':'OK'
    }
    return json_response(response)

@xframe_options_exempt
def ticket_embed(request, id):
    if Event.objects.filter(id = id, is_deleted = False).exists():
        event = Event.objects.get(id = id)
        tickets = Ticket.objects.filter(event = event, is_deleted = False).order_by('order', '-id')
        requiresAddress = False
        for ticket in tickets:
            if ticket.request_address:
                requiresAddress = True
            if ticket.extra_fields:
                custom_fields = simplejson.loads(ticket.extra_fields, object_pairs_hook=ordereddict.OrderedDict)
                fields = ordereddict.OrderedDict()
                for field_name, field_options in custom_fields.iteritems():
                    fields[field_name] = []
                    if field_options.strip() != '':
                        for option in field_options.split(','):
                            fields[field_name].append(option.strip())
                ticket.custom_fields = fields
        promos = Promo.objects.filter(event = event, is_deleted = False)
        organizers = Organizer.objects.filter(event = event)
    return render(request, 'event/ticket-embed.html', locals())

@login_required()
@validate('GET', ['id'])
def ticket(request, params, user):
    """
    Returns serialized data about the ticket
    """
    if not Ticket.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket does not exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    sold = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                        Q(purchase__checkout__is_charged = True, 
                                          purchase__checkout__is_refunded = False), 
                                        ticket = ticket).count()
    serialized = serialize_one(ticket)
    serialized['sold'] = sold
    response = {
        'status':'OK',
        'ticket':serialized
    }
    return json_response(response)

@login_required()
@validate('POST', 
          ['event', 'name', 'description'], 
          ['price', 'quantity', 'start_time', 'end_time', 'request_address', 'extra_fields'])
def create_ticket(request, params, user):
    """
    Create a ticket for an event
    """
    # Check if event is valid
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if ticket name is too long
    params['name'] = cgi.escape(params['name'])
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Ticket name cannot be over 50 characters.'
        }
        return json_response(response)
    # Check if the description is too long
    params['description'] = cgi.escape(params['description'])
    if len(params['description']) > 400:
        response = {
            'status':'FAIL',
            'error':'INVALID_DESCRIPTION',
            'message':'Ticket description cannot be over 400 characters.'
        }
        return json_response(response)
    ticket = Ticket(event = event, name = params['name'], 
                    description = params['description'])
    # Check price
    if params['price'] is not None:
        params['price'] = float(params['price'])
        if params['price'] < 0:
            response = {
                'status':'FAIL',
                'error':'NEGATIVE_PRICE',
                'message':'Price cannot be a negative number.'
            }
            return json_response(response)
        else:
            ticket.price = params['price']
    # Check quantity
    if params['quantity'] is not None:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] <= 0:
            response = {
                'status':'FAIL',
                'error':'NON_POSITIVE_QUANTITY',
                'message':'Quantity must be a positive integer.'
            }
            return json_response(response)
        else:
            ticket.quantity = params['quantity']
    # Check timing
    if params['start_time'] is not None:
        ticket.start_time = params['start_time']
    if params['end_time'] is not None:
        ticket.end_time = params['end_time']
    if ticket.end_time is not None:
        if (ticket.start_time is not None and 
            ticket.start_time > ticket.end_time):
            response = {
                'status':'FAIL',
                'error':'INVALID_TIMING',
                'message':'End time cannot be before start time.'
            }
            return json_response(response)
    if params['request_address']:
        if params['request_address'] == 'true':
            ticket.request_address = True
        if params['request_address'] == 'false':
            ticket.request_address = False
    # Extra fields
    if params['extra_fields'] is not None:
        try:
            fields = json.loads(params['extra_fields'])
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            ticket.extra_fields = json.dumps(fields)
    # All checks passed, write to database
    ticket.save()
    response = {
        'status':'OK',
        'ticket':serialize_one(ticket)
    }
    return json_response(response)

@login_required()
@validate('POST', 
          ['id'], 
          ['name', 'description', 'price', 'quantity', 'start_time', 
           'end_time', 'request_address', 'extra_fields'])
def edit_ticket(request, params, user):
    """
    Edit a ticket
    """
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['id'], 
                                 is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    event = ticket.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Go through all params and edit the ticket accordingly
    if params['name'] is not None:
        params['name'] = cgi.escape(params['name'])
        if not (0 < len(params['name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Ticket name cannot be blank or over 50 characters.'
            }
            return json_response(response)
        else:
            ticket.name = params['name']
    if params['description'] is not None:
        params['description'] = cgi.escape(params['description'])
        if not (0 < len(params['description']) <= 400):
            response = {
                'status':'FAIL',
                'error':'INVALID_DESCRIPTION',
                'message':'Ticket description must be between 0-400 characters.'
            }
            return json_response(response)
        else:
            ticket.description = params['description']
    if params['price'] is not None:
        params['price'] = float(params['price'])
        if params['price'] < 0:
            response = {
                'status':'FAIL',
                'error':'NEGATIVE_PRICE',
                'message':'Price cannot be a negative number.'
            }
            return json_response(response)
        else:
            ticket.price = params['price']
    if params['quantity'] is not None:
        if params['quantity'] == 'none':
            ticket.quantity = None
        else:
            params['quantity'] = int(params['quantity'])
            if params['quantity'] < 0:
                response = {
                    'status':'FAIL',
                    'error':'NEGATIVE_QUANTITY',
                    'message':'Quantity must be a non-negative integer.'
                }
                return json_response(response)
            else:
                ticket.quantity = params['quantity']
    if params['start_time'] is not None:
        if params['start_time'] == 'none':
            ticket.start_time = None
        else:
            ticket.start_time = params['start_time']
    if params['end_time'] is not None:
        if params['end_time'] == 'none':
            ticket.end_time = None
        else:
            ticket.end_time = params['end_time']
    if ticket.end_time is not None:
        if (ticket.start_time is not None and 
            ticket.start_time > ticket.end_time):
            response = {
                'status':'FAIL',
                'error':'INVALID_TIMING',
                'message':'End time cannot be before start time.'
            }
            return json_response(response)
    if params['request_address']:
        if params['request_address'] == 'true':
            ticket.request_address = True
        if params['request_address'] == 'false':
            ticket.request_address = False
    # Extra fields
    if params['extra_fields'] is not None:
        try:
            fields = simplejson.loads(params['extra_fields'], object_pairs_hook=ordereddict.OrderedDict)
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            ticket.extra_fields = json.dumps(fields)
    # Save the changes
    ticket.save()
    sold = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                        Q(purchase__checkout__is_charged = True, 
                                          purchase__checkout__is_refunded = False), 
                                        ticket = ticket).count()
    serialized = serialize_one(ticket)
    serialized['sold'] = sold
    response = {
        'status':'OK',
        'ticket':serialized
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete_ticket(request, params, user):
    """
    Delete a ticket
    """
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['id'], 
                                 is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    event = ticket.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Mark the ticket as deleted
    ticket.is_deleted = True
    ticket.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['event', 'details'])
def reorder_tickets(request, params, user):
    """
    Reorder Tickers

    @details: {'#ticket1.id':#order, '#ticket2.id':#order, ...}
    """
    # Check if user has permission for the event
    if not Organizer.objects.filter(event__id = params['event'], 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    details = None
    try:
        details = json.loads(params['details'])
    except ValueError:
        response = {
            'status':'FAIL',
            'error':'INVALID_DETAILS',
            'message':'The ticket details are not in legal format.'
        }
        return json_response(response)
    _details = {}
    for tid in details:
        _details[int(tid)] = int(details[tid])
    details = _details
    for tid in details:
        if Ticket.objects.filter(event__id = params['event'], id = tid).exists():
            ticket = Ticket.objects.get(event__id = params['event'], id = tid)
            ticket.order = details[tid]
            ticket.save()
        else:
            response = {
                'status':'FAIL',
                'error':'TICKET_DOESNT_EXIST',
                'message':'One of the tickets does not belong to this event'
            }
            return json_response(response)
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('GET', ['id'])
def promo(request, params, user):
    """
    Returns serialized data about the promo
    """
    if not Promo.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROMO_NOT_FOUND',
            'message':'The promo code does not exist.'
        }
        return json_response(response)
    promo = Promo.objects.get(id = params['id'])
    event = promo.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    response_promo = {}
    response_promo['id'] = promo.id
    response_promo['code'] = promo.code
    response_promo['amount'] = promo.amount
    response_promo['discount'] = promo.discount
    response_promo['email_domain'] = promo.email_domain
    response_promo['quantity'] = promo.quantity
    if promo.start_time:
        response_promo['start_time'] = promo.start_time.strftime('%m/%d/%Y')
    else:
        response_promo['start_time'] = None
    if promo.expiration_time:
        response_promo['expiration_time'] = promo.expiration_time.strftime('%m/%d/%Y')
    else:
        response_promo['expiration_time'] = None
    response_promo['tickets'] = []
    for ticket in promo.tickets.all():
        response_promo['tickets'].extend([ticket.id])
    response = {
        'status':'OK',
        'promo':response_promo
    }
    return json_response(response)

@login_required()
@validate('POST', ['event', 'code'], 
          ['amount', 'discount', 'email_domain', 'quantity', 'start_time', 'expiration_time'])
def create_promo(request, params, user):
    """
    Create a promo code
    """
    # Check if event is valid
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    params['code'] = cgi.escape(params['code'])
    if len(params['code']) > 20:
        response = {
            'status':'FAIL',
            'error':'INVALID_CODE',
            'message':'The code must be within 20 characters.'
        }
        return json_response(response)
    if ' ' in params['code']:
        response = {
            'status':'FAIL',
            'error':'INVALID_CODE',
            'message':'Code cannot contain spaces.'
        }
        return json_response(response)
    if Promo.objects.filter(code = params['code'], event = event).exists():
        response = {
            'status':'FAIL',
            'error':'DUPLICATE_CODE',
            'message':'You cannot have two identical promo codes.'
        }
        return json_response(response)
    amount = None
    if params['amount']:
        params['amount'] = float(params['amount'])
        if params['amount'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_AMOUNT',
                'message':'The discount amount must be a positive number.'
            }
            return json_response(response)
        else:
            amount = params['amount']
    discount = None
    if params['discount']:
        params['discount'] = float(params['discount'])
        if not (0 <= params['discount'] <= 1):
            response = {
                'status':'FAIL',
                'error':'INVALID_DISCOUNT',
                'message':'THe discount percentage must between 0 and 100 percent.'
            }
            return
        else:
            discount = params['discount']
    if amount is None and discount is None:
        response = {
            'status':'FAIL',
            'error':'MISSING_AMOUNT',
            'message':'You must have either a concrete amount or a percentage discount.'
        }
        return json_response(response)
    if params['email_domain']:
        params['email_domain'] = cgi.escape(params['email_domain'])
        if len(params['email_domain']) > 20:
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL_DOMAIN',
                'message':'The email domain is not valid.'
            }
            return json_response(response)
    else:
        params['email_domain'] = ''
    if params['quantity']:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'The quantity must be a non-negative integer.'
            }
            return json_response(response)
    else:
        params['quantity'] = None
    if params['start_time']:
        if params['start_time'] == 'none':
            params['start_time'] = None
        else:
            params['start_time'] = params['start_time']
    if params['expiration_time']:
        if params['expiration_time'] == 'none':
            params['expiration_time'] = None
        else:
            params['expiration_time'] = params['expiration_time']
    if params['start_time'] is not None and params['expiration_time'] is not None:
        if params['start_time'] >= params['expiration_time']:
            response = {
                'status':'FAIL',
                'error':'INVALID_TIMING',
                'message':'The timing is invalid.'
            }
            return json_response(response)
    promo = Promo(event = event, 
                  code = params['code'], 
                  amount = amount, 
                  discount = discount,
                  email_domain = params['email_domain'], 
                  quantity = params['quantity'], 
                  start_time = params['start_time'], 
                  expiration_time = params['expiration_time'])
    promo.save()
    response = {
        'status':'OK',
        'promo':serialize_one(promo)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['code', 'amount', 'discount', 'email_domain', 'quantity', 'start_time', 'expiration_time'])
def edit_promo(request, params, user):
    """
    Edit a promo code
    """
    if not Promo.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROMO_NOT_FOUND',
            'message':'The promo code does not exist.'
        }
        return json_response(response)
    promo = Promo.objects.get(id = params['id'])
    event = promo.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    if params['code'] is not None:
        if Promo.objects.filter(code = params['code'], event = event).exists() and promo.code != params['code']:
            response = {
                'status':'FAIL',
                'error':'DUPLICATE_CODE',
                'message':'You cannot have two identical promo codes.'
            }
            return json_response(response)
        params['code'] = cgi.escape(params['code'])
        if len(params['code']) > 20:
            response = {
                'status':'FAIL',
                'error':'INVALID_CODE',
                'message':'The code must be within 20 characters.'
            }
            return json_response(response)
        if ' ' in params['code']:
            response = {
                'status':'FAIL',
                'error':'INVALID_CODE',
                'message':'Code cannot contain spaces.'
            }
            return json_response(response)
        promo.code = params['code']
    if params['amount']:
        params['amount'] = float(params['amount'])
        if params['amount'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_AMOUNT',
                'message':'The discount amount must be a positive number.'
            }
            return json_response(response)
        else:
            promo.discount = None
            promo.amount = params['amount']
    if params['discount']:
        params['discount'] = float(params['discount'])
        if not (0 <= params['discount'] <= 1):
            response = {
                'status':'FAIL',
                'error':'INVALID_DISCOUNT',
                'message':'THe discount percentage must between 0 and 100 percent.'
            }
            return
        else:
            promo.amount = None
            promo.discount = params['discount']
    if promo.amount is None and promo.discount is None:
        response = {
            'status':'FAIL',
            'error':'MISSING_AMOUNT',
            'message':'You must have either a concrete amount or a percentage discount.'
        }
        return json_response(response)
    if params['email_domain'] is not None:
        params['email_domain'] = cgi.escape(params['email_domain'])
        if len(params['email_domain']) > 20:
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL_DOMAIN',
                'message':'The email domain is not valid.'
            }
            return json_response(response)
        promo.email_domain = params['email_domain']
    if params['quantity'] is not None and params['quantity'] != '':
        params['quantity'] = int(params['quantity'])
        if params['quantity'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'The quantity must be a non-negative integer.'
            }
            return json_response(response)
        promo.quantity = params['quantity']
    elif params['quantity'] == '':
        promo.quantity = None
    if params['start_time']:
        if params['start_time'] == 'none':
            promo.start_time = None
        else:
            promo.start_time = params['start_time']
    if params['expiration_time']:
        if params['expiration_time'] == 'none':
            promo.expiration_time = None
        else:
            promo.expiration_time = params['expiration_time']
    if promo.start_time is not None and promo.expiration_time is not None:
        if promo.start_time >= promo.expiration_time:
            response = {
                'status':'FAIL',
                'error':'INVALID_TIMING',
                'message':'The timing is invalid.'
            }
            return json_response(response)
    promo.save()
    if Purchase_promo.objects.filter(promo = promo).exists():
        amount_claimed = Purchase_promo.objects.filter(promo = promo).aggregate(Sum('quantity'))['quantity__sum']
    else:
        amount_claimed = 0
    response = {
        'status':'OK',
        'promo':serialize_one(promo),
        'claimed':amount_claimed
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'ticket'])
def link_promo(request, params, user):
    """
    Link a ticket with a promo code
    """
    if not Promo.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROMO_NOT_FOUND',
            'message':'The promo code does not exist.'
        }
        return json_response(response)
    promo = Promo.objects.get(id = params['id'])
    event = promo.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['ticket'], 
                                 event = event, is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'INVALID_TICKET',
            'message':'The ticket is invalid for this promo code.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['ticket'])
    tickets = promo.tickets.all()
    for _ticket in tickets:
        if _ticket.id == ticket.id:
            response = {
                'status':'OK',
                'error':'ALREADY_LINKED',
                'message':'The ticket is already linked with this promo code.'
            }
            return json_response(response)
    promo.tickets.add(ticket)
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'ticket'])
def unlink_promo(request, params, user):
    """
    Unlink a ticket from a promo code
    """
    if not Promo.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROMO_NOT_FOUND',
            'message':'The promo code does not exist.'
        }
        return json_response(response)
    promo = Promo.objects.get(id = params['id'])
    event = promo.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['ticket'], 
                                 event = event).exists():
        response = {
            'status':'FAIL',
            'error':'INVALID_TICKET',
            'message':'The ticket is invalid for this promo code.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['ticket'])
    promo.tickets.remove(ticket)
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete_promo(request, params, user):
    """
    Delete a promo code
    """
    if not Promo.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROMO_NOT_FOUND',
            'message':'The promo code does not exist.'
        }
        return json_response(response)
    promo = Promo.objects.get(id = params['id'])
    event = promo.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    promo.is_deleted = True
    promo.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def set_attachment(request, params, user):
    """
    Set the attachment for a ticket
    """
    if not Ticket.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket does not exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    if not request.FILES.has_key('attachment'):
        ticket.attachment = None
    else:
        # Validate the MIME type of the file
        ticket.attachment = request.FILES['attachment']
    ticket.save()
    response = {
        'status':'OK',
        'url': ticket.attachment.url
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def remove_attachment(request, params, user):
    """
    Remove the attachment for a ticket
    """
    if not Ticket.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket does not exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    ticket.attachment = None
    ticket.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@task()
def send_event_reminder(purchase, tz):
    sendEventReminder(purchase, tz)
    return True

@task()
def mark_purchase_as_expired(purchase, immediate=False):
    """
    Expires a purchase and release the tickets
    """
    # Update purchase object
    if not immediate:
        purchase = Purchase.objects.get(id = purchase.id)
    # Make sure the purchase isn't already marked as expired or charged
    if not purchase.is_expired and not purchase.checkout.is_charged:
        # Mark it as exipred
        purchase.is_expired = True
        purchase.save()
        # And update the ticket quantities if necessary
        items = Purchase_item.objects.filter(purchase = purchase) \
                                     .values('ticket') \
                                     .annotate(quantity = Count('id'))
        for item in items:
            tid = item['ticket']
            quantity = item['quantity']
            ticket = Ticket.objects.get(id = tid)
            if ticket.quantity is not None:
                Ticket.objects \
                      .filter(id = ticket.id) \
                      .update(quantity = F('quantity') + quantity)
    return True

@login_check()
@validate('POST', 
          ['event', 'email', 'first_name', 'last_name', 'details'], 
          ['phone', 'promos', 'address', 'invite'])
def purchase(request, params, user):
    """
    Make purchase for an event

    @details: {
        '#ticket1.id': {
            'quantity': #quantity,
            'extra_fields': {...} 
        },
        '#ticket2.id': {
            'quantity': #quantity,
            'extra_fields': {...}
        }
        ...
    }
    """
    _user = user
    # Check purchaser information
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    user, created = User.objects.get_or_create(email = params['email'])
    if len(params['first_name']) > 50 or len(params['last_name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Your first or last name is too long.'
        }
        return json_response(response)
    if user.password is None or (_user is not None and _user.id == user.id):
        user.first_name = params['first_name']
        user.last_name = params['last_name']
    if params['phone'] is not None:
        params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
        if len(params['phone']) != 10:
            response = {
                'status':'FAIL',
                'error':'INVALID_PHONE',
                'message':'Your phone number is invalid.'
            }
            return json_response(response)
        if (user.password is None or 
            (_user is not None and _user.id == user.id)):
            user.phone = params['phone']
    # Save the user details after all other checks are done
    # Check purchase details
    details = None
    try:
        details = json.loads(params['details'])
    except ValueError:
        response = {
            'status':'FAIL',
            'error':'INVALID_DETAILS',
            'message':'The purchase details are not in legal format.'
        }
        return json_response(response)
    # Check if the event is valid
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    # Check if the tickets are valid
    _tickets = Ticket.objects.filter(event = event, is_deleted = False)
    tickets = {}
    for _ticket in _tickets:
        if len(_ticket.extra_fields) == 0:
            _ticket.extra_fields = None
        else:
            _ticket.extra_fields = json.loads(_ticket.extra_fields)
        tickets[_ticket.id] = _ticket
    address = ''
    if params['address']:
        address = params['address']
    _details = {}
    for tid in details:
        _details[int(tid)] = details[tid]
    details = _details
    for tid in details:
        # Check if the ticket belongs to the event
        if tickets.has_key(tid):
            ticket = tickets[tid]
            if ticket.request_address and (params['address'] is None or len(params['address']) == 0):
                response = {
                    'status':'FAIL',
                    'error':'INVALID_ADDRESS',
                    'message':'An address is needed for certain tickets.'
                }
                return json_response(response)
            now = timezone.now()
            # Check timing
            if ((ticket.start_time is None or ticket.start_time <= now) and 
                (ticket.end_time is None or ticket.end_time >= now)):
                # Check quantity
                if details[tid]['quantity'] > 0:
                    # Check extra fields
                    if ticket.extra_fields is not None:
                        for fieldName, fieldValue in ticket.extra_fields.iteritems():
                            if not details[tid]['extra_fields'].has_key(fieldName):
                                response = {
                                    'status':'FAIL',
                                    'error':'MISSING_EXTRA_FIELDS',
                                    'message':'The extra fields are incomplete for some tickets.'
                                }
                                return json_response(response)
                            if len(fieldValue) != 0:
                                options = fieldValue.split(',')
                                options = [x.lstrip() for x in options]
                                if str(details[tid]['extra_fields'][fieldName]) not in options:
                                    response = {
                                        'status':'FAIL',
                                        'error':'EXTRA_FIELDS_MISMATCH',
                                        'message':'Some field values do not match the field options.'
                                    }
                                    return json_response(response)
                            continue
                    else:
                        details[tid]['extra_fields'] = ''
                        continue
                else:
                    response = {
                        'status':'FAIL',
                        'error':'INVALID_QUANTITY',
                        'message':'Quantity must be a positive number.'
                    }
                    return json_response(response)
        else:
            response = {
                'status':'FAIL',
                'error':'INVALID_TICKET',
                'message':'One of the ticket is invalid.'
            }
            return json_response(response)
    # Check if the promo codes are valid
    promos = []
    if params['promos'] is not None:
        codes = params['promos'].split(',')
        for code in codes:
            if Promo.objects.filter(code = code, 
                                    event = event.id, 
                                    is_deleted = False).exists():
                promo = Promo.objects.get(code = code, is_deleted = False)
                if promo.start_time is None or promo.start_time <= timezone.now():
                    if promo.expiration_time is None or promo.expiration_time >= timezone.now():
                        l = len(promo.email_domain)
                        if params['email'][-l:] == promo.email_domain or l == 0:
                            pTIds = []
                            pTickets = promo.tickets.all()
                            for pTicket in pTickets:
                                pTIds.append(pTicket.id)
                            promos.append({
                                'promo':promo,
                                'tickets':pTIds,
                                'quantity':0
                            })
                            continue
            response = {
                'status':'FAIL',
                'error':'INVALID_PROMO',
                'message':'One of the promo codes is invalid.'
            }
            return json_response(response)
    # Sum up the quantities needed for promos
    for tid, detail in details.items():
        for i in range(0, len(promos)):
            if tid in promos[i]['tickets']:
                promos[i]['quantity'] += detail['quantity']
    # Check if it exceeds the limit of the promo codes
    for promo in promos:
        if promo['promo'].quantity is not None:
            if promo['promo'].quantity - promo['quantity'] < 0:
                response = {
                    'status': 'FAIL',
                    'error': 'INSUFFICIENT_QUANTITY',
                    'message': 'Some of the promo codes are no longer valid.'
                }
                return json_response(response)
    # Check if there is an unfinished purchase
    if Purchase.objects.filter(Q(checkout__isnull = False, 
                                 checkout__is_charged = False), 
                               owner = user, event = event, 
                               is_expired = False).exists():
        # If so, release its holding quantity if necessary
        purchases = Purchase.objects.filter(Q(checkout__isnull = False, 
                                          checkout__is_charged = False), 
                                        owner = user, event = event, 
                                        is_expired = False)
        # Mark the old purchase as expired
        for purchase in purchases:
            mark_purchase_as_expired(purchase, True)
    # Start a database transaction
    with transaction.atomic():
        # Place a lock on the ticket information (quantity)
        tids = details.keys()
        tickets = Ticket.objects.select_for_update().filter(id__in = tids)
        # Calculate the aggregate amount
        amount = 0
        for ticket in tickets:
            # Check if the ticket has enough quantity left
            if (ticket.quantity is not None and 
                ticket.quantity < details[ticket.id]['quantity']):
                response = {
                    'status':'FAIL',
                    'error':'INSUFFICIENT_QUANTITY',
                    'message':'There aren\'t enough tickets left.'
                }
                return json_response(response)
            priceA = ticket.price
            priceB = ticket.price
            for promo in promos:
                if ticket.id in promo['tickets']:
                    if promo['promo'].amount is not None:
                        priceA -= promo['promo'].amount
                    elif promo['promo'].discount is not None:
                        if ticket.price * promo['promo'].discount <= priceB:
                            priceB = ticket.price * (1 - promo['promo'].discount)
            if priceA < priceB:
                amount += priceA * details[ticket.id]['quantity']
            else:
                amount += priceB * details[ticket.id]['quantity']
        # All checks done, save user information
        user.save()
        # Check if the purchase is in fact an RSVP action (free)
        if amount == 0:
            # Create the purchase
            purchase = Purchase(owner = user, event = event, amount = 0)
            if params['invite']:
                if Invite.objects.filter(id = params['invite']).exists():
                    purchase.invite = Invite.objects.get(id = params['invite'])
            purchase.save()
            for ticket in tickets:
                for i in range(0, details[ticket.id]['quantity']):
                    item = Purchase_item(purchase = purchase, 
                                         ticket = ticket, 
                                         price = ticket.price, 
                                         address = address, 
                                         extra_fields = json.dumps(details[ticket.id]['extra_fields']))
                    item.save()
                # If the ticket has a quantity limit
                if ticket.quantity is not None:
                    # Update the ticket quantity
                    Ticket.objects \
                          .filter(id = ticket.id) \
                          .update(quantity = F('quantity') - details[ticket.id]['quantity'])
            for promo in promos:
                item = Purchase_promo(purchase = purchase, 
                                      promo = promo['promo'], 
                                      quantity = promo['quantity'])
                item.save()
                if promo['promo'].quantity is not None:
                    Promo.objects.filter(id = promo['promo'].id) \
                                 .update(quantity = F('quantity') - promo['quantity'])
            items = {}
            for ticket in purchase.items.all():
                if ticket.id in items:
                    items[ticket.id]['quantity'] += 1
                else:
                    items[ticket.id] = {
                        'name': ticket.name,
                        'quantity': 1
                    }
            # Send confirmation email and sms
            sendEventConfirmationEmail(purchase)
            if timezone.now() < (event.start_time - timedelta(days = 1)):
                dayBefore = event.start_time - timedelta(days = 1)
                send_event_reminder.apply_async(args = [purchase, timezone.get_current_timezone()], eta = dayBefore)
            if params['phone'] is not None:
                sendEventConfirmationSMS(purchase)
            # Success
            response = {
                'status':'OK',
                'purchase':serialize_one(purchase),
                'tickets': items
            }
            return json_response(response)
        # Otherwise
        # Get the event creator's payemnt account
        creator = Organizer.objects.get(event = event, 
                                        is_creator = True).profile
        paymentAccount = creator.payment_account
        # Create the checkout
        checkout = Checkout(payer = user, 
                            payee = paymentAccount, 
                            amount = amount, 
                            description = event.name)
        checkout.save()
        # Create the purchase
        purchase = Purchase(owner = user, event = event, amount = amount, 
                            checkout = checkout)
        if params['invite']:
                if Invite.objects.filter(id = params['invite']).exists():
                    purchase.invite = Invite.objects.get(id = params['invite'])
        purchase.save()
        for promo in promos:
            purchase.promos.add(promo['promo'])
        purchase.save()
        for ticket in tickets:
            for i in range(0, details[ticket.id]['quantity']):
                item = Purchase_item(purchase = purchase, 
                                     ticket = ticket, 
                                     price = ticket.price, 
                                     address = address, 
                                     extra_fields = details[ticket.id]['extra_fields'])
                item.save()
            # If the ticket has a quantity limit
            if ticket.quantity is not None:
                # Update the ticket quantity
                Ticket.objects \
                      .filter(id = ticket.id) \
                      .update(quantity = F('quantity') - details[ticket.id]['quantity'])
        for promo in promos:
            item = Purchase_promo(purchase = purchase, 
                                  promo = promo['promo'], 
                                  quantity = promo['quantity'])
            item.save()
            if promo['promo'].quantity is not None:
                Promo.objects.filter(id = promo['promo'].id) \
                             .update(quantity = F('quantity') - promo['quantity'])
        # Create an async task to restore quantities if necessary
        expiration = timezone.now() + timedelta(minutes = BBOY_TRANSACTION_EXPIRATION)
        mark_purchase_as_expired.apply_async(args = [purchase], eta = expiration)
        # Check for creator logo
        if creator.image:
            creator_logo = creator.image.source.url.split("?")[0]
        else:
            creator_logo = None
        # All done, send publishable key to create client checkout
        response = {
            'status':'OK',
            'purchase':serialize_one(purchase),
            'publishable_key':paymentAccount.publishable_key,
            'logo':creator_logo
        }
        return json_response(response)
    # If it gets here, there is a transaction failure
    response = {
        'status':'FAIL',
        'error':'FAILED_TRANSACTION',
        'message':'The transaction failed, please try again.'
    }
    return json_response(response)

@login_required()
@validate('POST', ['event', 'details', 'email', 'first_name', 'last_name'], 
          ['phone', 'address', 'force', 'send_email'])
def add_purchase(request, params, user):
    """
    Manually add purchase by organizer

    @details: {
        '#ticket1.id': {
            'quantity': #quantity,
            'extra_fields': {...} 
        },
        '#ticket2.id': {
            'quantity': #quantity,
            'extra_fields': {...}
        }
        ...
    }
    """
    _user = user
    # Check purchaser information
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    user, created = User.objects.get_or_create(email = params['email'])
    if (not REGEX_NAME.match(params['first_name']) or 
        not REGEX_NAME.match(params['last_name'])):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Your first or last name contain illegal characters.'
        }
        return json_response(response)
    if len(params['first_name']) > 50 or len(params['last_name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Your first or last name is too long.'
        }
        return json_response(response)
    if user.password is None or (_user is not None and _user.id == user.id):
        user.first_name = params['first_name']
        user.last_name = params['last_name']
    if params['phone'] is not None:
        params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
        if len(params['phone']) != 10:
            response = {
                'status':'FAIL',
                'error':'INVALID_PHONE',
                'message':'Your phone number is invalid.'
            }
            return json_response(response)
        if (user.password is None or 
            (_user is not None and _user.id == user.id)):
            user.phone = params['phone']
    # Save the user details after all other checks are done
    # Check purchase details
    details = None
    try:
        details = json.loads(params['details'])
    except ValueError:
        response = {
            'status':'FAIL',
            'error':'INVALID_DETAILS',
            'message':'The purchase details are not in legal format.'
        }
        return json_response(response)
    # Check if the event is valid
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    if not Organizer.objects.filter(event = event, profile__managers = _user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    else:
        inviter = Organizer.objects.filter(event = event, profile__managers = _user)[0]
    # Check for duplicate email
    if Purchase.objects.filter(event = event, owner__email = params['email']).exists():
        if not params['force'] or params['force'] != 'true':
            response = {
                'status':'WAIT',
                'error':'DUPLICATE_EMAIL',
                'message':'This email is already registered for the event. Would you like to add the guest anyways?'
            }
            return json_response(response)
    # Check if the tickets are valid
    _tickets = Ticket.objects.filter(event = event, is_deleted = False)
    tickets = {}
    for _ticket in _tickets:
        if len(_ticket.extra_fields) == 0:
            _ticket.extra_fields = None
        else:
            _ticket.extra_fields = json.loads(_ticket.extra_fields)
        tickets[_ticket.id] = _ticket
    address = ''
    if params['address']:
        address = params['address']
    _details = {}
    for tid in details:
        _details[int(tid)] = details[tid]
    details = _details
    for tid in details:
        # Check if the ticket belongs to the event
        if tickets.has_key(tid):
            ticket = tickets[tid]
            if ticket.request_address and (params['address'] is None or len(params['address']) == 0):
                response = {
                    'status':'FAIL',
                    'error':'INVALID_ADDRESS',
                    'message':'An address is needed for certain tickets.'
                }
                return json_response(response)
            now = timezone.now()
            # Check timing
            if ((ticket.start_time is None or ticket.start_time <= now) and 
                (ticket.end_time is None or ticket.end_time >= now)):
                # Check quantity
                if details[tid]['quantity'] > 0:
                    # Check extra fields
                    if ticket.extra_fields is not None:
                        for fieldName, fieldValue in ticket.extra_fields.iteritems():
                            if not details[tid]['extra_fields'].has_key(fieldName.strip()):
                                response = {
                                    'status':'FAIL',
                                    'error':'MISSING_EXTRA_FIELDS',
                                    'message':'The extra fields are incomplete for some tickets.'
                                }
                                return json_response(response)
                            if len(fieldValue) != 0:
                                options = fieldValue.split(',')
                                options = [x.lstrip() for x in options]
                                if str(details[tid]['extra_fields'][fieldName.strip()]) not in options:
                                    response = {
                                        'status':'FAIL',
                                        'error':'EXTRA_FIELDS_MISMATCH',
                                        'message':'Some field values do not match the field options.'
                                    }
                                    return json_response(response)
                            continue
                    else:
                        details[tid]['extra_fields'] = ''
                        continue
                else:
                    response = {
                        'status':'FAIL',
                        'error':'INVALID_QUANTITY',
                        'message':'Quantity must be a positive number.'
                    }
                    return json_response(response)
        else:
            response = {
                'status':'FAIL',
                'error':'INVALID_TICKET',
                'message':'One of the ticket is invalid.'
            }
            return json_response(response)
    # Start a database transaction
    with transaction.atomic():
        # Place a lock on the ticket information (quantity)
        tids = details.keys()
        tickets = Ticket.objects.select_for_update().filter(id__in = tids)
        # Calculate the aggregate amount
        amount = 0
        for ticket in tickets:
            # Check if the ticket has enough quantity left
            if (ticket.quantity is not None and 
                ticket.quantity < details[ticket.id]['quantity']):
                response = {
                    'status':'FAIL',
                    'error':'INSUFFICIENT_QUANTITY',
                    'message':'There aren\'t enough tickets left.'
                }
                return json_response(response)
        # All checks done, save user information
        user.save()
        # Create the purchase
        purchase = Purchase(owner = user, event = event, amount = 0)
        purchase.save()
        for ticket in tickets:
            for i in range(0, details[ticket.id]['quantity']):
                item = Purchase_item(purchase = purchase, 
                                     ticket = ticket, 
                                     price = ticket.price, 
                                     address = address, 
                                     extra_fields = json.dumps(details[ticket.id]['extra_fields']))
                item.save()
            # If the ticket has a quantity limit
            if ticket.quantity is not None:
                # Update the ticket quantity
                Ticket.objects \
                      .filter(id = ticket.id) \
                      .update(quantity = F('quantity') - details[ticket.id]['quantity'])
        items = {}
        for ticket in purchase.items.all():
            if ticket.id in items:
                items[ticket.id]['quantity'] += 1
            else:
                items[ticket.id] = {
                    'name': ticket.name,
                    'quantity': 1
                }
        # Send confirmation email and sms
        if params['send_email'] and params['send_email'] == 'true':
            sendEventConfirmationEmail(purchase, True, inviter)
            #sendEventConfirmationSMS(purchase)
        # Success
        response = {
            'status':'OK',
            'purchase':serialize_one(purchase),
            'tickets': items
        }
        return json_response(response)
    # If it gets here, there is a transaction failure
    response = {
        'status':'FAIL',
        'error':'FAILED_TRANSACTION',
        'message':'The transaction failed, please try again.'
    }
    return json_response(response)

@login_required()
@validate('GET', ['id'])
def export(request, params, user):
    """
    Export the purchase items into csv
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, profile__managers = user, is_creator = True).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_PRIMARY_ORGANIZER',
            'message':'Only the primary organizer of an event can export the guest list.'
        }
        return json_response(response)
    # Get all successful purchases
    purchase_items = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                        Q(purchase__checkout__is_charged = True, 
                                          purchase__checkout__is_refunded = False), 
                                        purchase__event = event, 
                                        purchase__is_expired = False).order_by('ticket__id')
    items = {
        'tickets': {}
    }
    for item in purchase_items:
        # If ticket in tickets
        if item.ticket.id in items['tickets']:
            # If purchase in ticket
            if item.purchase.id in items['tickets'][item.ticket.id]['purchases']:
                items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['quantity'] += 1
            else:
                if item.is_checked_in:
                    checked_in = 'yes'
                else:
                    checked_in = ''
                items['tickets'][item.ticket.id]['purchases'][item.purchase.id] = {
                    'id': item.id,
                    'email': item.purchase.owner.email,
                    'first_name': item.purchase.owner.first_name,
                    'last_name': item.purchase.owner.last_name,
                    'code': item.purchase.code,
                    'checked_in': checked_in,
                    'quantity': 1
                }
                if item.ticket.request_address:
                    if item.address:
                        items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['address'] = item.address
                    else:
                        items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['address'] = ''
                if item.ticket.extra_fields != '':
                    try:
                        extra_fields = json.loads(item.ticket.extra_fields)
                    except:
                        pass
                    finally:
                        try:
                            item.extra_fields = item.extra_fields.replace("\'", "\"")
                            item.extra_fields = item.extra_fields.replace("u\"", "\"")
                            item.extra_fields = item.extra_fields.replace("\"d", "\'d")
                            item.extra_fields = item.extra_fields.replace("\"s", "\'s")
                            item_fields = json.loads(item.extra_fields)
                        except:
                            pass
                        finally:
                            if type(item_fields) is dict:
                                items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['extra_fields'] = {}
                                for fieldName, fieldValue in extra_fields.iteritems():
                                    if fieldName in item_fields:
                                        items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['extra_fields'][fieldName] = item_fields[fieldName]
                                    else:
                                        items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['extra_fields'][fieldName] = 'N/A'
        # If ticket NOT in tickets
        else:
            if item.is_checked_in:
                checked_in = 'yes'
            else:
                checked_in = ''
            items['tickets'][item.ticket.id] = {
                'id': item.ticket.id,
                'name': item.ticket.name,
                'request_address': item.ticket.request_address,
                'purchases': {
                    item.purchase.id: {
                        'id': item.id,
                        'email': item.purchase.owner.email,
                        'first_name': item.purchase.owner.first_name,
                        'last_name': item.purchase.owner.last_name,
                        'code': item.purchase.code,
                        'checked_in': checked_in,
                        'quantity': 1
                    }
                }
            }
            if item.ticket.request_address:
                if item.address:
                    items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['address'] = item.address
                else:
                    items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['address'] = ''
            if item.ticket.extra_fields != '':
                try:
                    extra_fields = json.loads(item.ticket.extra_fields)
                finally:
                    items['tickets'][item.ticket.id]['extra_fields'] = {}
                    for fieldName, fieldValue in extra_fields.iteritems():
                        items['tickets'][item.ticket.id]['extra_fields'][fieldName] = fieldName
                try:
                    item.extra_fields = item.extra_fields.replace("\'", "\"")
                    item.extra_fields = item.extra_fields.replace("u\"", "\"")
                    item.extra_fields = item.extra_fields.replace("\"d", "\'d")
                    item.extra_fields = item.extra_fields.replace("\"s", "\'s")
                    item_fields = json.loads(item.extra_fields)
                except:
                    item_fields = {}
                finally:
                    items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['extra_fields'] = {}
                    for fieldName, fieldValue in extra_fields.iteritems():
                        if fieldName in item_fields:
                            items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['extra_fields'][fieldName] = item_fields[fieldName]
                        else:
                            items['tickets'][item.ticket.id]['purchases'][item.purchase.id]['extra_fields'][fieldName] = 'N/A'
            else:
                items['tickets'][item.ticket.id]['extra_fields'] = None
    # Prepare csv writer and the response headers
    response = HttpResponse(mimetype = 'text/csv')
    csvName = re.sub(r'\W+', '-', event.name) + '.csv'
    response['Content-Disposition'] = 'attachment; filename="' + csvName + '"'
    writer = UnicodeWriter(response)
    # Write to csv
    count = 1
    for k, ticket in items['tickets'].iteritems():
        headers = ['id', 'email', 'first_name', 'last_name', 'ticket', 'quantity', 'code', 'checked in']
        if ticket['request_address']:
            headers.append('address')
        if ticket['extra_fields'] is not None:
            for k, field in ticket['extra_fields'].iteritems():
                headers.append(field)
        if count > 1:
            writer.writerow([])
        writer.writerow(headers)
        for k, item in ticket['purchases'].iteritems():
            row = [
                str(count),
                item['email'],
                item['first_name'],
                item['last_name'],
                ticket['name'],
                str(item['quantity']),
                item['code'],
                item['checked_in']
            ]
            if ticket['request_address']:
                row.append(item['address'])
            if ticket['extra_fields'] is not None:
                if 'extra_fields' in item:
                    for fieldName, fieldValue in item['extra_fields'].iteritems():
                        row.append(str(fieldValue))
            writer.writerow(row)
            count += 1
    return response

@login_required()
@validate('POST', ['id'], ['cancel'])
def checkin(request, params, user):
    """
    Check in a purchase item
    """
    # Check if the purchase item exists
    if not Purchase_item.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PURCHASE_ITEM_NOT_FOUND',
            'message':'The purchase item doesn\'t exist.'
        }
        return json_response(response)
    item = Purchase_item.objects.get(id = params['id'])
    event = item.purchase.event
    # Check if user has permission for the event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check in or cancel checkin
    if params['cancel'] is not None:
        item.is_checked_in = False
        item.checked_in_time = None
    else:
        if not item.is_checked_in:
            item.is_checked_in = True
            item.checked_in_time = timezone.now()
    item.save()
    response = {
        'status':'OK',
        'item':serialize_one(item)
    }
    return json_response(response)