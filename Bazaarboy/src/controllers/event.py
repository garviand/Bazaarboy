"""
Controller for events
"""

import cgi
import json
import os
import re
from datetime import timedelta
from django.db import transaction, IntegrityError
from django.db.models import F, Q, Count
from django.http import Http404
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.core.serializers.json import DjangoJSONEncoder
from celery import task
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.csvutils import UnicodeWriter
from src.email import sendEventConfirmationEmail
from src.regex import REGEX_EMAIL
from src.sanitizer import sanitize_redactor_input
from src.serializer import serialize, serialize_one
from src.sms import sendEventConfirmationSMS

@cache_page(60 * 5)
@login_check()
@validate('GET', [], ['preview', 'design'])
def index(request, id, params, user):
    """
    Event page
    """
    if not Event.objects.filter(id = id, is_deleted = False).exists():
        raise Http404
    event = Event.objects.select_related().get(id = id)
    editable = (user is not None and 
                Organizer.objects.filter(event = event, 
                                         profile__managers = user).exists())
    preview = params['preview'] is not None and editable
    design = params['design'] is not None and editable
    if not design and not preview and not event.is_launched:
        return redirect('index')
    tickets = Ticket.objects.filter(event = event, is_deleted = False)
    organizers = Organizer.objects.filter(event = event)
    rsvp = True
    cheapest = float('inf')
    for ticket in tickets:
        if ticket.price > 0:
            rsvp = False
        if ticket.price < cheapest:
            cheapest = ticket.price
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
                                    profile__managers = user).exists():
        return redirect('index')
    if step == 'tickets':
        tickets = Ticket.objects.filter(event = event, is_deleted = False)
        tickets = list(tickets)
        for i in range(0, len(tickets)):
            sold = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                                Q(purchase__checkout__is_charged = True, 
                                                  purchase__checkout__is_refunded = False), 
                                                ticket = tickets[i]).count()
            tickets[i].sold = sold
        promos = Promo.objects.filter(event = event, is_deleted = False)
    return render(request, 'event/modify-' + step + '.html', locals())

@login_required()
@validate('GET')
def manage(request, id, params, user):
    if not Event.objects.filter(id = id).exists():
        raise Http404
    event = Event.objects.get(id = id)
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        return redirect('index')
    purchases = Purchase_item.objects.filter(Q(purchase__checkout = None) | 
                                        Q(purchase__checkout__is_charged = True, 
                                          purchase__checkout__is_refunded = False), 
                                        purchase__event = event, 
                                        purchase__is_expired = False).order_by('-id')
    tickets = Ticket.objects.filter(event=event)
    checked_in = purchases.exclude(Q(checked_in_time = None)).count()
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
                                        is_expired = False).annotate(rsvps=Count('items'))
        
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

@validate('GET', ['keyword'])
def search(request, params):
    """
    Search events by keyword
    """
    events = Event.objects.filter(name__icontains = params['keyword'], 
                                  is_deleted = False)
    response = {
        'status':'OK',
        'events':serialize(events)
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
    event.save()
    # Set the profile as the organizer and creator of the event
    organizer = Organizer(event = event, profile = profile, is_creator = True)
    organizer.save()
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
           'longitude'])
def edit(request, params, user):
    """
    Edit an existing event
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
        event.start_time = params['start_time']
    if params['end_time'] is not None:
        if params['end_time'] == 'none':
            event.end_time = None
        else:
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
    # Save the changes
    event.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'profile'])
def add_organizer(request, params, user):
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
    response = {
        'status':'OK'
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
    # Launch the event
    event.is_launched = True
    event.launched_time = timezone.now()
    event.save()
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
    response = {
        'status':'OK'
    }
    return json_response(response)

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
          ['price', 'quantity', 'start_time', 'end_time'])
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
    if len(params['description']) > 250:
        response = {
            'status':'FAIL',
            'error':'INVALID_DESCRIPTION',
            'message':'Ticket description cannot be over 150 characters.'
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
           'end_time'])
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
        if not (0 < len(params['description']) <= 250):
            response = {
                'status':'FAIL',
                'error':'INVALID_DESCRIPTION',
                'message':'Ticket description must be between 0-250 characters.'
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
    # Save the changes
    ticket.save()
    response = {
        'status':'OK',
        'ticket':serialize_one(ticket)
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
@validate('POST', ['ticket', 'code', 'amount', 'email_domain'])
def create_promo(request, params, user):
    """
    Create a promo code
    """
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['ticket'], 
                                 is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['ticket'])
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
    params['code'] = cgi.escape(params['code'])
    if len(params['code']) > 20:
        response = {
            'status':'FAIL',
            'error':'INVALID_CODE',
            'message':'The code must be within 20 characters.'
        }
        return json_response(response)
    if Promo.objects.filter(code = params['code'], event = event).exists():
        response = {
            'status':'FAIL',
            'error':'DUPLICATE_CODE',
            'message':'You cannot have two identical promo codes.'
        }
        return json_response(response)
    params['amount'] = float(params['amount'])
    if params['amount'] < 0 or ticket.price - params['amount'] < 0:
        response = {
            'status':'FAIL',
            'error':'INVALID_AMOUNT',
            'message':'The discount amount can be at most the ticket price.'
        }
        return json_response(response)
    params['email_domain'] = cgi.escape(params['email_domain'])
    if params['email_domain'] > 20:
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL_DOMAIN',
            'message':'The email domain is not valid.'
        }
        return json_response(response)
    promo = Promo(event = event, ticket = ticket, 
                  code = params['code'], 
                  amount = params['amount'], 
                  email_domain = params['email_domain'])
    promo.save()
    response = {
        'status':'OK',
        'promo':serialize_one(promo)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'code', 'amount', 'email_domain'])
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
        params['code'] = cgi.escape(params['code'])
        if len(params['code']) > 20:
            response = {
                'status':'FAIL',
                'error':'INVALID_CODE',
                'message':'The code must be within 20 characters.'
            }
            return json_response(response)
        promo.code = params['code']
    if params['amount'] is not None:
        params['amount'] = float(params['amount'])
        if params['amount'] < 0 or ticket.price - params['amount'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_AMOUNT',
                'message':'The discount amount can be at most the ticket price.'
            }
            return json_response(response)
        promo.amount = params['amount']
    if params['email_domain'] is not None:
        params['email_domain'] = cgi.escape(params['email_domain'])
        if params['email_domain'] > 20:
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL_DOMAIN',
                'message':'The email domain is not valid.'
            }
            return json_response(response)
        promo.email_domain = params['email_domain']
    promo.save()
    response = {
        'status':'OK',
        'promo':serialize_one(response)
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
        for tid, quantity in items.iteritems():
            ticket = Ticket.objects.get(id = tid)
            if ticket.quantity is not None:
                Ticket.objects \
                      .filter(id = ticket.id) \
                      .update(quantity = F('quantity') + quantity)
    return True

@login_check()
@validate('POST', 
          ['event', 'email', 'first_name', 'last_name', 'details'], 
          ['phone', 'promos'])
def purchase(request, params, user):
    """
    Make purchase for an event

    @details: {'#ticket1.id':#quantity, '#ticket2.id':#quantity, ...}
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
        details = json.loads(details)
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
        tickets[_ticket.id] = _ticket
    for tid in details:
        details[tid] = int(details[tid])
        # Check if the ticket belongs to the event
        if tickets.has_key(int(tid)):
            ticket = tickets[tid]
            now = timezone.now()
            # Check timing
            if ((ticket.start_time is None or ticket.start_time <= now) and 
                (ticket.end_time is None or ticket.end_time >= now)):
                # Check quantity
                if details[tid] > 0:
                    continue
                else:
                    response = {
                        'status':'FAIL',
                        'error':'INVALID_QUANTITY',
                        'message':'Quantity must be a positive number.'
                    }
                    return json_response(response)
        response = {
            'status':'FAIL',
            'error':'INVALID_TICKET',
            'message':'One of the ticket is invalid.'
        }
        return json_response(response)
    # Check if the promo codes are valid
    promos = {}
    if params['promos'] is not None:
        codes = params['promos'].split(',')
        for code in codes:
            if Promo.objects.filter(code = code, event = event, 
                                    is_deleted = False).exists():
                promo = Promo.objects.get(code = code, event = event)
                if not promo.ticket.is_deleted:
                    l = len(promo.email_domain)
                    if params['email'][-l:] == promo.email_domain:
                        promos[promo.ticket.id] = promo
                        continue
            response = {
                'status':'FAIL',
                'error':'INVALID_PROMO',
                'message':'One of the promo codes is invalid.'
            }
            return json_response(response)
    # Check if there is an unfinished purchase
    if Purchase.objects.filter(Q(checkout__isnull = False, 
                                 checkout__is_charged = False), 
                               owner = user, event = event, 
                               is_expired = False).exists():
        # If so, release its holding quantity if necessary
        purchase = Purchase.objects.get(Q(checkout__isnull = False, 
                                          checkout__is_charged = False), 
                                        owner = user, event = event, 
                                        is_expired = False)
        # Mark the old purchase as expired
        mark_purchase_as_expired(purchase, True)
    # Start a database transaction
    with transaction.commit_on_success():
        # Place a lock on the ticket information (quantity)
        tids = details.keys()
        tickets = Ticket.objects.select_for_update().filter(id__in = tids)
        # Calculate the aggregate amount
        amount = 0
        for ticket in tickets:
            # Check if the ticket has enough quantity left
            if (ticket.quantity is not None and 
                ticket.quantity < details[ticket.id]):
                response = {
                    'status':'FAIL',
                    'error':'INSUFFICIENT_QUANTITY',
                    'message':'There aren\'t enough tickets left.'
                }
                return json_response(response)
            price = ticket.price
            if promos.has_key(ticket.id):
                price -= promos[ticket.id].amount
            amount += price * details[ticket.id]
        # All checks done, save user information
        user.save()
        # Check if the purchase is in fact an RSVP action (free)
        if amount == 0:
            # Create the purchase
            purchase = Purchase(owner = user, event = event, amount = 0)
            purchase.save()
            for promo in promos.itervalue():
                purchase.promos.add(promo)
            purchase.save()
            for ticket in tickets:
                for i in range(0, details[ticket.id]):
                    item = Purchase_item(purchase = purchase, 
                                         ticket = ticket, 
                                         price = ticket.price)
                    item.save()
                    items.append(item)
                # If the ticket has a quantity limit
                if ticket.quantity is not None:
                    # Update the ticket quantity
                    Ticket.objects \
                          .filter(id = ticket.id) \
                          .update(quantity = F('quantity') - details[ticket.id])
            # Send confirmation email and sms
            sendEventConfirmationEmail(purchase)
            sendEventConfirmationSMS(purchase)
            # Success
            response = {
                'status':'OK',
                'purchase':serialize_one(purchase)
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
        purchase.save()
        for promo in promos.itervalue():
            purchase.promos.add(promo)
        purchase.save()
        for ticket in tickets:
            for i in range(0, details[ticket.id]):
                item = Purchase_item(purchase = purchase, 
                                     ticket = ticket, 
                                     price = ticket.price)
                item.save()
            # If the ticket has a quantity limit
            if ticket.quantity is not None:
                # Update the ticket quantity
                Ticket.objects \
                      .filter(id = ticket.id) \
                      .update(quantity = F('quantity') - details[ticket.id])
        # Create an async task to restore quantities if necessary
        expiration = timezone.now() + timedelta(minutes = BBOY_TRANSACTION_EXPIRATION)
        mark_purchase_as_expired.apply_async(args = [purchase], eta = expiration)
        # All done, send publishable key to create client checkout
        response = {
            'status':'OK',
            'purchase':serialize_one(purchase),
            'publishable_key':paymentAccount.publishable_key
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
@validate('POST', ['details', 'email', 'first_name', 'last_name'], ['phone'])
def add_purchase(request, params, user):
    """
    Manually add purchase by organizer
    """
    pass

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
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Get all successful purchases
    purchases = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = event)
    pids = [purchase.id for purchase in purchases]
    # Get all relevant purchase items
    items = Purchase_item.objects.select_related('purchase__owner', 'ticket') \
                                 .filter(purchase__in = pids)
    # Prepare csv writer and the response headers
    response = HttpResponse(mimetype = 'text/csv')
    csvName = re.sub(r'\W+', '-', event.name) + '.csv'
    response['Content-Disposition'] = 'attachment; filename="' + csvName + '"'
    writer = UnicodeWriter(response)
    headers = ['id', 'email', 'first_name', 'last_name', 'ticket', 'code']
    writer.writerow(headers)
    # Write to csv
    for i in range(1, items.count() + 1):
        item = items[i - 1]
        row = [
            i, 
            item.purchase.owner.email, 
            item.purchase.owner.first_name, 
            item.purchase.owner.last_name, 
            item.ticket.name, 
            item.code
        ]
        writer.writerow(row)
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