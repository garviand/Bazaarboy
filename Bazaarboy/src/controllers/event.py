"""
Controller for events
"""

import os
import re
from datetime import timedelta
from django.db import transaction, IntegrityError
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from celery import task
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.csvutils import UnicodeWriter
from src.email import Email
from src.regex import REGEX_EMAIL
from src.sanitizer import sanitize_redactor_input
from src.serializer import serialize, serialize_one
from src.sms import SMS

@cache_page(60 * 5)
@login_check()
@validate('GET', [], ['token', 'preview'])
def index(request, id, params, user):
    """
    Event page
    """
    if not Event.objects.filter(id = id).exists():
        raise Http404
    preview = False
    if params['preview'] is not None:
        user = None
        preview = True
    event = Event.objects.select_related().get(id = id)
    editable = False
    if Event_organizer.objects.filter(event = event).count() != 0:
        editable = (user is not None and 
                    Event_organizer.objects.filter(event = event, 
                                                   profile__managers = user) \
                                           .exists())
        if not editable and not event.is_launched and not preview:
            return redirect('index')
    elif params['token'] is not None and event.access_token == params['token']:
        editable = True
    else:
        return redirect('index')
    tickets = Ticket.objects.filter(event = event)
    rsvp = True
    cheapest = float('inf')
    for ticket in tickets:
        if ticket.price > 0:
            rsvp = False
        if ticket.price < cheapest:
            cheapest = ticket.price
    organizers = Event_organizer.objects.filter(event = event)
    return render(request, 'event/index.html', locals())

@login_required()
@validate('GET')
def manage(request, id, params, user):
    if not Event.objects.filter(id = id).exists():
        raise Http404
    event = Event.objects.get(id = id)
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user).exists():
        return redirect('index')
    purchases = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = event, 
                                        is_expired = False).order_by('-id')
    tickets = Ticket.objects.filter(event=event)
    checked_in = purchases.exclude(Q(checked_in_time = None)).count()
    return render(request, 'event/manage.html', locals())

@login_required()
@validate('GET', ['id'])
def event(request, params, user):
    """
    Return serialized data for the event
    """
    if not Event.objects.filter(id = params['id']).exists():
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
    events = Event.objects.filter(name__icontains = params['keyword'])
    response = {
        'status':'OK',
        'events':serialize(events)
    }
    return json_response(response)

@login_check()
@validate('POST', [], ['profile'])
def create(request, params, user):
    """
    Create a new event
    """
    event = Event(name = 'Untitled Event', 
                  start_time = timezone.now() + timedelta(days = 7))
    # Check if the user has logged in
    if user is not None:
        # If so, check if the profile is valid
        if params['profile'] is None:
            response = {
                'status':'FAIL',
                'error':'MISSING_PROFILE',
                'message':'A profile is required to create an event.'
            }
            return json_response(response)
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
        # Save to database
        event.save()
        # Set the profile as the organizer and creator of the event
        organizer = Event_organizer(event = event, profile = profile, 
                                    is_creator = True)
        organizer.save()
    else:
        # Otherwise, generate an access token for the anonymous user
        event.access_token = os.urandom(32).encode('base_64')[:32]
        # Save to database
        event.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id'], 
          ['name', 'description', 'cover', 'caption', 'summary', 'tags', 
           'start_time', 'end_time', 'location', 'latitude', 'longitude', 
           'category', 'is_private', 'token'])
def edit(request, params, user):
    """
    Edit an existing event
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has logged in
    if user is not None:
        # If so, check if user has permission for the event
        if not Event_organizer.objects.filter(event = event, 
                                              profile__managers = user) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if params['token'] is None or event.access_token != params['token']:
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    # Go through all the params and edit the event accordingly
    if params['name'] is not None:
        if not (0 < len(params['name']) <= 150):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Event name cannot be blank or over 50 characters.'
            }
            return json_response(response)
        else:
            event.name = params['name']
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
    if params['summary'] is not None:
        if len(params['summary']) > 100:
            response = {
                'status':'FAIL',
                'error':'SUMMARY_TOO_LONG',
                'message':'The summary must be within 150 characters.'
            }
            return json_response(response)
        else:
            event.summary = params['summary']
    if params['tags'] is not None:
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
        if (params['end_time'] is not None and 
            params['end_time'] != 'none' and
            params['end_time'] < params['start_time']):
            response = {
                'status':'FAIL',
                'error':'INVALID_START_TIME',
                'message':'The start time cannot be after the end time.'
            }
            return json_response(response)
        else:
            event.start_time = params['start_time']
    if params['end_time'] is not None:
        if params['end_time'] == 'none':
            event.end_time = None
        elif params['end_time'] < params['start_time']:
            response = {
                'status':'FAIL',
                'error':'INVALID_END_TIME',
                'message':'The end time cannot be before the start time.'
            }
            return json_response(response)
        else:
            tickets = Ticket.objects.filter(event = event)
            for ticket in tickets:
                if ticket.end_time == event.end_time:
                    ticket.end_time = params['end_time']
                    ticket.save()
            event.end_time = params['end_time']
    if params['location'] is not None:
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
        event.category = params['category']
    if params['is_private'] is not None:
        event.is_private = params['is_private']
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
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
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
    if Event_organizer.objects.filter(event = event, profile = profile).exists():
        response = {
            'status':'FAIL',
            'error':'ALREADY_AN_ORGANIZER',
            'message':'The profile is already an organizer.'
        }
        return json_response(response)
    # Add the profile as an organizer
    organizer = Event_organizer(event = event, profile = profile)
    organizer.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'profile'])
def delete_organizer(request, params, user):
    # Check if the event is valid
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
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
    if not Event_organizer.objects.filter(event = event, profile = profile) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_AN_ORGANIZER',
            'message':'The profile is not an organizer.'
        }
        return json_response(response)
    organizer = Event_organizer.objects.get(event = event, profile = profile)
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
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check if the event has started
    if event.start_time <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'STARTED_EVENT',
            'message':'The start time of the event has passed.'
        }
        return json_response(response)
    # Launch the event
    event.is_launched = True
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
    Take an event offline and refund all tickets
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
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
    # Check if the event has started
    if event.start_time <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'STARTED_EVENT',
            'message':'You cannot take a started event offline.'
        }
        return json_response(response)
    # Refund all purchases
    tickets = Ticket.objects.filter(event = event)
    for ticket in tickets:
        pass
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
def syncToFB(request, params, user):
    pass

@login_check()
@validate('POST', ['id'], ['token'])
def delete(request, params, user):
    """
    Delete an event
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user is logged in
    if user is not None:
        # If so, check if user has permission for the event
        if not Event_organizer.objects.filter(event = event, 
                                              profile__managers = user) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if params['token'] is None or event.access_token != params['token']:
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    # Check if the event is launched
    if event.is_launched:
        response = {
            'status':'FAIL',
            'error':'LAUNCHED_EVENT',
            'message':'The event is launched, please take it offline first.'
        }
        return json_response(response)
    # Delete the event and all its tickets
    Ticket.objects.filter(event = event).delete()
    event.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('POST', 
          ['event', 'name', 'description'], 
          ['price', 'quantity', 'start_time', 'end_time', 'token'])
def create_ticket(request, params, user):
    """
    Create a ticket for an event
    """
    # Check if event is valid
    if not Event.objects.filter(id = params['event']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    # Check if user is logged in
    if user is not None:
        # If so, check if user has permission for the event
        if not Event_organizer.objects.filter(event = event, 
                                              profile__managers = user) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if params['token'] is None or event.access_token != params['token']:
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    # Check if ticket name is too long
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Ticket name cannot be over 50 characters.'
        }
        return json_response(response)
    # Check if the description is too long
    if len(params['description']) > 150:
        response = {
            'status':'FAIL',
            'error':'INVALID_DESCRIPTION',
            'message':'Ticket description cannot be over 150 characters.'
        }
        return json_response(response)
    # Check if the event has started
    if event.start_time <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'STARTED_EVENT',
            'message':'You cannot add a ticket to a started event.'
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
        if params['start_time'] >= event.start_time:
            response = {
                'status':'FAIL',
                'error':'INVALID_START_TIME',
                'message':'The start time is invalid.'
            }
            return json_response(response)
        else:
            ticket.start_time = params['start_time']
    if params['end_time'] is not None:
        if ((event.end_time is None and 
             params['end_time'] > event.start_time) or  
            (event.end_time is not None and 
             params['end_time'] > event.end_time) or 
             params['end_time'] <= ticket.start_time):
            response = {
                'status':'FAIL',
                'error':'INVALID_END_TIME',
                'message':'The end time is invalid.'
            }
            return json_response(response)
        else:
            ticket.end_time = params['end_time']
    # All checks passed, write to database
    ticket.save()
    response = {
        'status':'OK',
        'ticket':serialize_one(ticket)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id'], 
          ['name', 'description', 'price', 'quantity', 'start_time', 
           'end_time', 'token'])
def edit_ticket(request, params, user):
    """
    Edit a ticket
    """
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    event = ticket.event
    # Check if user is logged in
    if user is not None:
        # If so, check if user has permission for the event
        if not Event_organizer.objects.filter(event = event, 
                                              profile__managers = user) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if params['token'] is None or event.access_token != params['token']:
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    # Go through all params and edit the ticket accordingly
    if params['name'] is not None:
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
        if not (0 < len(params['description']) <= 150):
            response = {
                'status':'FAIL',
                'error':'INVALID_DESCRIPTION',
                'message':'Ticket description must be between 0-150 characters.'
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
        if params['quantity'].lower() == 'none':
            ticket.quantity = None
        else:
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
    if params['start_time'] is not None:
        if params['start_time'] >= event.start_time:
            response = {
                'status':'FAIL',
                'error':'INVALID_START_TIME',
                'message':'The start time is invalid.'
            }
            return json_response(response)
        else:
            ticket.start_time = params['start_time']
    if params['end_time'] is not None:
        if ((event.end_time is not None and 
             params['end_time'] > event.end_time) or 
            (event.end_time is None and 
             params['end_time'] > event.start_time) or
            (ticket.start_time is not None and 
             params['end_time'] <= ticket.start_time)):
            response = {
                'status':'FAIL',
                'error':'INVALID_END_TIME',
                'message':'The end time is invalid.'
            }
            return json_response(response)
        else:
            ticket.end_time = params['end_time']
    # Save the changes
    ticket.save()
    response = {
        'status':'OK',
        'ticket':serialize_one(ticket)
    }
    return json_response(response)

@login_check()
@validate('POST', ['id'], ['token'])
def delete_ticket(request, params, user):
    """
    Delete a ticket
    """
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['id'])
    event = ticket.event
    # Check if user is logged in
    if user is not None:
        # If so, check if user has permission for the event
        if not Event_organizer.objects.filter(event = event, 
                                              profile__managers = user) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if params['token'] is None or event.access_token != params['token']:
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the event.'
            }
            return json_response(response)
    # Check if the event has started
    if event.is_launched and event.start_time <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'STARTED_EVENT',
            'message':'You cannot delete the ticket for a started event.'
        }
        return json_response(response)
    # Refund all purchases for the ticket
    purchases = Purchase.objects.filter(ticket = ticket)
    for purchase in purchases:
        pass
    # Delete the ticket
    ticket.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@task()
def mark_purchase_as_expired(purchase):
    """
    Expires a purchase after some time and release the ticket
    """
    # Update purchase object
    purchase = Purchase.objects.get(id = purchase.id)
    # Make sure the purchase isn't already marked as expired or 
    # charged
    if not purchase.is_expired and not purchase.checkout.is_charged:
        # Mark it as exipred
        purchase.is_expired = True
        purchase.save()
        # And update the ticket quantity if necessary
        ticket = purchase.ticket
        if ticket.quantity is not None:
            Ticket.objects.filter(id = ticket.id) \
                          .update(quantity = F('quantity') + purchase.quantity)
    return True

def get_seats(seats, quantity, continuous=True):
    """
    Try probing the seats list to get the best continuous seats that fit with 
    the quantity
    """
    def get_seat(seat):
        i = re.search(r'\d', seat)
        if i:
            row = seat[:i.start()]
            number = int(seat[i.start():])
            return row, number
        else:
            return False, False
    results = []
    indexes = []
    count = 0
    prev = None
    if len(seats) < quantity:
        return False, False
    if not continuous:
        return seats[:quantity], seats[quantity:]
    for i in range(0, len(seats)):
        seat = seats[i]
        if prev is not None:
            currRow, currNum = get_seat(seat)
            prevRow, prevNum = get_seat(prev)
            if currRow == False or prevRow == False:
                return False, False
            else:
                if currRow != prevRow or prevNum + 1 != currNum:
                    count = 0
                    results = []
                    indexes = []
        count = count + 1
        prev = seat
        results.append(seat)
        indexes.append(i)
        if count == quantity:
            rest = []
            for j in range(0, len(seats)):
                if not j in indexes:
                    rest.append(seats[j])
            return results, rest
    return get_seats(seats, quantity, False)

@login_check()
@validate('POST', ['ticket', 'quantity'], ['email', 'full_name', 'phone'])
def purchase(request, params, user):
    """
    Purchase a ticket
    """
    # Check login status
    if user is None:
        if params['email'] is None:
            response = {
                'status':'FAIL',
                'error':'MISSING_EMAIL',
                'message':'You need an email to purchase the ticket.'
            }
            return json_response(response)
        if not REGEX_EMAIL.match(params['email']):
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL',
                'message':'Email format is invalid.'
            }
            return json_response(response)
        user, created = User.objects.get_or_create(email = params['email'])
        if not (user.password is None and user.fb_id is None):
            response = {
                'status':'FAIL',
                'error':'EMAIL_EXISTS',
                'message':'This email collides with an existing account.'
            }
            return json_response(response)
        if params['full_name'] is None:
            response = {
                'status':'FAIL',
                'error':'MISSING_FULL_NAME',
                'message':'You need your full name to purchase the ticket.'
            }
            return json_response(response)
        if not (0 < len(params['full_name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Your full name cannot be blank or over 50 chars.'
            }
            return json_response(response)
        user.full_name = params['full_name']
        if params['phone'] is not None:
            params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
            if len(params['phone']) != 10:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_PHONE',
                    'message':'Your phone number is invalid.'
                }
                return json_response(response)
            user.phone = params['phone']
        user.save()
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['ticket']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['ticket'])
    event = ticket.event
    # Check if the event is launched
    if not event.is_launched:
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_LAUNCHED',
            'message':'The event is not launched yet.'
        }
        return json_response(response)
    # Check if the ticket is up for sale
    if not (ticket.start_time <= timezone.now() <= ticket.end_time):
        response = {
            'status':'FAIL',
            'error':'INVALID_TICKET',
            'message':'The ticket is not up for sale at this time.'
        }
        return json_response(response)
    # Check if the quantity is valid
    params['quantity'] = int(params['quantity'])
    if params['quantity'] <= 0:
        response = {
            'status':'FAIL',
            'error':'INVALID_QUANTITY',
            'message':'The quantity must be bigger than zero.'
        }
        return json_response(response)
    # Check if there is an exisiting purchase
    if Purchase.objects.filter(Q(checkout = None) | 
                               Q(checkout__is_charged = True, 
                                 checkout__is_refunded = False), 
                               owner = user, event = event, 
                               is_expired = False).exists():
        response = {
            'status':'FAIL',
            'error':'PURCHASED_ALREADY',
            'message':'You have already bought a ticket to the event.'
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
        purchase.is_expired = True
        purchase.save()
        # Restore quantity
        if purchase.ticket.quantity is not None:
            Ticket.objects.filter(id = purchase.ticket.id) \
                          .update(quantity = F('quantity') + purchase.quantity)
    # Start a database transaction
    with transaction.commit_on_success():
        # Place a lock on the ticket information (quantity)
        ticket = Ticket.objects.select_for_update().filter(id = ticket.id)[0]
        # Check if the ticket has enough quantity
        if ticket.quantity is not None and ticket.quantity < params['quantity']:
            response = {
                'status':'FAIL',
                'error':'INSUFFICIENT_QUANTITY',
                'message':'There aren\'t enough tickets left.'
            }
            return json_response(response)
        # Check if it's a free ticket
        if ticket.price == 0:
            # Create the purchase
            purchase = Purchase(owner = user, ticket = ticket, event = event, 
                                price = ticket.price, 
                                quantity = params['quantity'])
            purchase.save()
            # If the ticket has a quantity limit
            if ticket.quantity is not None:
                # Update the ticket quantity
                Ticket.objects \
                      .filter(id = ticket.id) \
                      .update(quantity = F('quantity') - purchase.quantity)
            # Assign seats
            if ticket.seats is not None:
                seats = ticket.seats.split(',')
                assigned, rest = get_seats(seats, purchase.quantity)
                if assigned:
                    # Seat assigned
                    purchase.seats = ','.join(assigned)
                    purchase.save()
                    # Update the ticket seats
                    Ticket.objects.filter(id = ticket.id) \
                                  .update(seats = ','.join(rest))
                else:
                    # Assign seats failed, raise exception to roll back
                    raise IntegrityError()
            # Try sending the confirmation email
            email = Email()
            email.sendPurchaseConfirmationEmail(purchase)
            if len(user.phone) == 10:
                # Try sending the confirmation text
                try:
                    sms = SMS()
                    sms.sendPurchaseConfirmationSMS(purchase)
                except Exception:
                    pass
            response = {
                'status':'OK',
                'purchase':serialize_one(purchase)
            }
            return json_response(response)
        # If it's not a free ticket
        # Get the event creator's payemnt account
        creator = Event_organizer.objects.get(event = event, 
                                              is_creator = True) \
                                         .profile
        paymentAccount = creator.payment_account
        # Calculate checkout total
        amount = ticket.price * params['quantity']
        # Create the checkout
        checkoutDescription = '%s - %s' % (event.name, ticket.name)
        checkout = Checkout(payer = user, 
                            payee = paymentAccount, 
                            amount = amount, 
                            description = checkoutDescription)
        checkout.save()
        # Create the purchase
        purchase = Purchase(owner = user, ticket = ticket, event = event, 
                            price = ticket.price, 
                            quantity = params['quantity'], 
                            checkout = checkout)
        purchase.save()
        # If the ticket has a quantity limit
        if ticket.quantity is not None:
            # Schedule the purchase to be expired after some amount of time
            expiration = timezone.now()
            expiration += timedelta(minutes = BBOY_TRANSACTION_EXPIRATION)
            mark_purchase_as_expired.apply_async(args = [purchase], 
                                                 eta = expiration)
            # Update the ticket quantity
            Ticket.objects \
                  .filter(id = ticket.id) \
                  .update(quantity = F('quantity') - purchase.quantity)
        if creator.image:
            creator_logo = creator.image.source.url
        else:
            creator_logo = None
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
@validate('POST', ['ticket', 'email'], ['full_name', 'phone'])
def add_purchase(request, params, user):
    # Check if the ticket is valid
    if not Ticket.objects.filter(id = params['ticket']).exists():
        response = {
            'status':'FAIL',
            'error':'TICKET_NOT_FOUND',
            'message':'The ticket doesn\'t exist.'
        }
        return json_response(response)
    ticket = Ticket.objects.get(id = params['ticket'])
    event = ticket.event
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Attempt to get or create the corresponding user
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    user, created = User.objects.get_or_create(email = params['email'])
    if created:
        if params['full_name'] is None:
            response = {
                'status':'FAIL',
                'error':'MISSING_FULL_NAME',
                'message':'You need a full name to add a purchase.'
            }
            return json_response(response)
        if not (0 < len(params['full_name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'The full name cannot be blank or over 50 chars.'
            }
            return json_response(response)
        user.full_name = params['full_name']
        if params['phone'] is not None:
            params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
            if len(params['phone']) != 10:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_PHONE',
                    'message':'The phone number is invalid.'
                }
                return json_response(response)
            user.phone = params['phone']
        user.save()
    # Check if there is an exisiting purchase
    if Purchase.objects.filter(Q(checkout = None) | 
                               Q(checkout__is_charged = True, 
                                 checkout__is_refunded = False), 
                               owner = user, event = event, 
                               is_expired = False).exists():
        response = {
            'status':'FAIL',
            'error':'PURCHASED_ALREADY',
            'message':'This email has already bought a ticket to the event.'
        }
        return json_response(response)
    shouldDeductQuantity = True
    # Check if there is an unfinished purchase
    if Purchase.objects.filter(Q(checkout__isnull = False, 
                                 checkout__is_charged = False), 
                               owner = user, event = event, 
                               is_expired = False).exists():
        shouldDeductQuantity = False
    # Check if the ticket is sold out
    elif ticket.quantity is not None and ticket.quantity == 0:
        response = {
            'status':'FAIL',
            'error':'TICKET_SOLD_OUT',
            'message':'This ticket is sold out.'
        }
        return json_response(response)
    # Create the purchase
    purchase = Purchase(owner = user, ticket = ticket, event = event, 
                        price = 0)
    purchase.save()
    # If the ticket has a quantity limit
    if ticket.quantity is not None:
        # Adjust the ticket quantity
        ticket.quantity = F('quantity') - 1
        ticket.save()
    # Try sending the confirmation email
    try:
        email = Email()
        email.sendPurchaseConfirmationEmail(purchase)
    except Exception:
        pass
    if len(user.phone) == 10:
        # Try sending the confirmation text
        try:
            sms = SMS()
            sms.sendPurchaseConfirmationSMS(purchase)
        except Exception:
            pass
    response = {
        'status':'OK',
        'purchase':serialize_one(purchase)
    }
    return json_response(response)

@login_required()
@validate('GET', ['id'])
def purchase_csv(request, params, user):
    """
    Output the purchase list in csv format
    """
    # Check if the event is valid
    if not Event.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['id'])
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Get all the successful purchases
    purchases = Purchase.objects.filter(Q(event = params['id']), 
                                        Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False)) \
                                .order_by('ticket__name')
    # Output to csv
    csvName = re.sub(r'\W+', '-', event.name) + '.csv'
    response = HttpResponse(mimetype = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + csvName + '"'
    writer = UnicodeWriter(response)
    headers = ['name', 'email', 'ticket', 'code', 'quantity']
    writer.writerow(headers)
    for purchase in purchases:
        row = [
            purchase.owner.full_name, 
            purchase.owner.email, 
            purchase.ticket.name, 
            purchase.code,
            str(purchase.quantity)
        ]
        writer.writerow(row)
    return response

@login_required()
@validate('POST', ['id'], ['cancel', 'token'])
def checkin(request, params, user):
    # Check if the purchase exists
    if not Purchase.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PURCHASE_NOT_FOUND',
            'message':'The purchase doesn\'t exist.'
        }
        return json_response(response)
    purchase = Purchase.objects.get(id = params['id'])
    event = purchase.event
    # Check if user has permission for the event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Check in or cancel checkin
    if params['cancel'] is not None:
        purchase.is_checked_in = False
        purchase.checked_in_time = None
    else:
        if not purchase.is_checked_in:
            purchase.is_checked_in = True
            purchase.checked_in_time = timezone.now()
    purchase.save()
    response = {
        'status':'OK',
        'purchase':serialize_one(purchase)
    }
    return json_response(response)

@login_required()
@validate('GET')
def invite(request, id, params, user):
    if not Event.objects.filter(id = id).exists():
        raise Http404
    event = Event.objects.get(id = id)
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user).exists():
        return redirect('index')
    return render(request, 'event/invite.html', locals())
