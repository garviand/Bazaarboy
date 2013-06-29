"""
Controller for normal events
"""

from datetime import datetime, timedelta
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

import pdb

@login_check()
def index(request, id, loggedIn):
    """
    Normal event page
    """
    if not Event.objects.filter(id = id).exists():
        return Http404
    event = Event.objects.get(id = id)
    return render(request, 'event.html', locals())

@login_required()
@validate('GET', ['id'])
def event(request, params):
    """
    Return serialized data for the normal event
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

@login_required()
@validate('POST', 
          ['profile', 'name', 'description', 'start_time', 'location', 
           'category'], 
          ['end_time', 'latitude', 'longitude', 'is_private'])
def create(request, params):
    """
    Create a new normal event
    """
    # Check if the profile is valid
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    user = User.objects.get(id = request.session['user'])
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the profile.'
        }
        return json_response(response)
    # Check start and end time
    if (params['start_time'] < timezone.now() or 
        (params['end_time'] is not None and 
         params['end_time'] <= params['start_time'])):
        response = {
            'status':'FAIL',
            'error':'INVALID_TIME',
            'message':'The timing is invalid.'
        }
    # Validated, create the model
    event = Event(name = params['name'], 
                  description = params['description'], 
                  start_time = params['start_time'], 
                  end_time = params['end_time'], 
                  location = params['location'], 
                  category = params['category'], 
                  owner = profile)
    # Check if coordinates are specified, and if so, if they are legal
    if (params['latitude'] is not None and 
        params['longitude'] is not None and 
        not (-90.0 <= float(params['latitude']) <= 90.0 and 
             -180.0 <= float(params['longitude']) <= 180.0)):
        response = {
            'status':'FAIL',
            'error':'INVALID_COORDINATES',
            'message':'Latitude/longitude combination is invalid.'
        }
        return json_response(response)
    else:
        # Valid coordinates, set to event
        event.latitude = float(params['latitude'])
        event.longitude = float(params['longitude'])
    # Check if it's a private event
    if params['is_private'] is not None:
        event.is_private = params['is_private']
    # Save to database
    event.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['description', 'start_time', 'end_time', 'location', 'latitude', 
           'longitude', 'category', 'is_private'])
def edit(request, params):
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
    event = Event.objects.get(id = params['event'])
    # Check if user has permission for the event
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    # Go through all the params and edit the event accordingly
    if params['description'] is not None:
        if len(params['description']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_DESCRIPTION',
                'message':'Description cannot be blank.'
            }
            return json_response(response)
        else:
            event.description = params['description']
    if params['start_time'] is not None:
        if params['start_time'] < timezone.now():
            response = {
                'status':'FAIL',
                'error':'INVALID_START_TIME',
                'message':'The start time is invalid.'
            }
            return json_response(response)
        else:
            event.start_time = params['start_time']
    if params['end_time'] is not None:
        if params['end_time'] < params['start_time']:
            response = {
                'status':'FAIL',
                'error':'INVALID_END_TIME',
                'message':'The end time is invalid.'
            }
            return json_response(response)
        else:
            event.end_time = params['end_time']
    if params['location'] is not None:
        if len(params['location']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_LOCATION',
                'message':'Location cannot be blank.'
            }
            return json_response(response)
        else:
            event.location = params['location']
    if (params['latitude'] is not None and 
        params['longitude'] is not None and 
        not (-90.0 <= float(params['latitude']) <= 90.0 and 
             -180.0 <= float(params['longitude']) <= 180.0)):
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
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(event)

@login_required()
@validate('POST', ['id'])
def delete(request, params):
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
    event = Event.objects.get(id = params['event'])
    # Check if user has permission for the event
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
            'message':'You cannot delete a started event.'
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

@login_required()
@validate('POST', ['id'])
def launch(request, params):
    """
    Launch an event
    """
    pass

@login_required()
@validate('POST', ['id'])
def delaunch(request, params):
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
    event = Event.objects.get(id = params['event'])
    # Check if user has permission for the event
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
            'message':'You cannot take a started event offline.'
        }
        return json_response(response)
    # Refund all tickets
    tickets = Ticket.objects.filter(event = event)
    for ticket in tickets:
        pass
    # Mark the event as offline
    event.is_launched = False
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)

@login_required()
@validate('POST', 
          ['event', 'name', 'description'], 
          ['price', 'quantity', 'start_time', 'end_time'])
def create_ticket(request, params):
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
    # Check if user has permission for the event
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
        if (params['end_time'] >= event.start_time or 
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
    # All checks passed, write to database
    ticket.save()
    response = {
        'status':'OK',
        'ticket':serialize_one(ticket)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'price', 'quantity', 'start_time', 
           'end_time'])
def edit_ticket(request, params):
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
    # Check if the user has permission for the event
    user = User.objects.get(id = request.session['user'])
    event = ticket.event
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
            'message':'You cannot make changes to a started event.'
        }
        return json_response(response)
    # Go through all params and edit the ticket accordingly
    if params['name'] is not None:
        if len(params['name']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_NAME',
                'message':'Ticket name cannot be blank.'
            }
            return json_response(response)
        else:
            ticket.name = params['name']
    if params['description'] is not None:
        if len(params['description']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_DESCRIPTION',
                'message':'Ticket description cannot be blank.'
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
        if (params['end_time'] >= event.start_time or 
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

@login_required()
@validate('POST', ['id'])
def delete_ticket(request, params):
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
    # Check if the user has permission for the event
    user = User.objects.get(id = request.session['user'])
    event = ticket.event
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
            'message':'You cannot make changes to a started event.'
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