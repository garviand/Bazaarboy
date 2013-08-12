"""
Controller for events
"""

import os
from datetime import timedelta
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from celery import task
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.controllers.wepay import create_checkout
from src.sanitizer import sanitize_redactor_input
from src.serializer import serialize_one

@login_check()
@validate('GET', [], ['token'])
def index(request, id, params, user):
    """
    Event page
    """
    if not Event.objects.filter(id = id).exists():
        raise Http404
    event = Event.objects.select_related().get(id = id)
    editable = False
    if event.owner is not None:
        editable = (user is not None and 
                    Profile_manager.objects.filter(user = user, 
                                                   profile = event.owner) \
                                           .exists())
        if not editable and not event.is_launched:
            return redirect('index')
    elif params['token'] is not None and event.access_token == params['token']:
        editable = True
    else:
        return redirect('index')
    return render(request, 'event/index.html', locals())

@login_check()
def new(request, user):
    """
    Create event page
    """
    categories = BBOY_EVENT_CATEGORIES
    if user is not None:
        profiles = Profile.objects.filter(managers = user)
    return render(request, 'event/create.html', locals())

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

@login_check()
@validate('POST', 
          ['name', 'description', 'start_time', 'location', 'category'], 
          ['end_time', 'latitude', 'longitude', 'is_private', 'profile'])
def create(request, params, user):
    """
    Create a new event
    """
    # Check if the event name is too long
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Event name cannot be over 50 characters.'
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
                  description = sanitize_redactor_input(params['description']), 
                  start_time = params['start_time'], 
                  end_time = params['end_time'], 
                  location = params['location'], 
                  category = params['category'])
    # Check if coordinates are specified, and if so, if they are legal
    if params['latitude'] is not None and params['longitude'] is not None:
        if not (-90.0 <= float(params['latitude']) <= 90.0 and 
                -180.0 <= float(params['longitude']) <= 180.0):
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
    # Check if the user has logged in
    if user is not None:
        # If so, check if the profile is valid
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
        # Set the owner of the event to the specified profile
        event.owner = profile
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
          ['name', 'description', 'start_time', 'end_time', 'location', 
           'latitude', 'longitude', 'category', 'is_private', 'token'])
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
        if not Profile_manager.objects.filter(user = user, 
                                              profile = event.owner).exists():
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
        if not (0 < len(params['name']) <= 50):
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
    if params['latitude'] is not None and params['longitude'] is not None: 
        if not (-90.0 <= float(params['latitude']) <= 90.0 and 
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
    if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
        if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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

@login_required()
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
        if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
        if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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
    if event.start_time <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'STARTED_EVENT',
            'message':'You cannot make changes to a started event.'
        }
        return json_response(response)
    # Go through all params and edit the ticket accordingly
    if params['name'] is not None:
        if not (0 < len(params['name']) <= 15):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Ticket name cannot be blank or over 15 characters.'
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
        user = User.objects.get(id = request.session['user'])
        if not Profile_manager.objects.filter(user = user, profile = event.owner) \
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

@task()
def mark_purchase_as_expired(purchase):
    """
    Expires a purchase after some time and release the ticket
    """
    if not purchase.checkout.is_captured:
        purchase.is_expired = True
        purchase.save()
        ticket = purchase.ticket
        if ticket.quantity is not None:
            ticket.quantity = F('quantity') + 1
            ticket.save()
    return True

@login_check()
@validate('POST', ['ticket'], ['email'])
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
        user, created = User.objects.get_or_create(email = params['email'])
        if not (user.password is None and user.fb_id is None):
            response = {
                'status':'FAIL',
                'error':'EMAIL_EXISTS',
                'message':'This email collides with an existing account.'
            }
            return json_response(response)
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
    # Check if the event has started
    if event.start_time <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'STARTED_EVENT',
            'message':'You can\'t buy ticket to a started event.'
        }
        return json_response(response)
    # Check if the ticket is sold out
    if ticket.quantity is not None and ticket.quantity == 0:
        response = {
            'status':'FAIL',
            'error':'TICKET_SOLD_OUT',
            'message':'This ticket is sold out.'
        }
        return json_response(response)
    # Check if it's a free ticket
    if ticket.price == 0:
        # Check if there ia an existing purchase
        if Purchase.objects.filter(owner = user, event = event, 
                                   checkout = None, is_expired = False) \
                           .exists():
            response = {
                'status':'FAIL',
                'error':'PURCHASED_ALREADY',
                'message':'You have already bought a ticket to the event.'
            }
            return json_response(response)
        # Make the purchase record
        purchase = Purchase(owner = user, ticket = ticket, event = event, 
                            price = ticket.price)
        purchase.save()
        response = {
            'status':'OK',
            'purchase':serialize_one(purchase)
        }
        return json_response(response)
    # Check if there is an exisiting purchase
    if Purchase.objects.filter(Q(checkout = None) | 
                               Q(checkout__is_captured = True, 
                                 checkout__is_refunded = False), 
                               owner = user, event = event, 
                               is_expired = False).exists():
        response = {
            'status':'FAIL',
            'error':'PURCHASED_ALREADY',
            'message':'You have already bought a ticket to the event.'
        }
        return json_response(response)
    # All checks passed, request a checkout on WePay
    checkoutDescription = '%s - %s' % (event.name, ticket.name)
    checkoutInfo = create_checkout('EVENT', 
                                   event.owner.wepay_account.accound_id, 
                                   checkoutDescription, ticket.price)
    checkout = Wepay_checkout(payer = user, payee = event.owner.wepay_account, 
                              checkout_id = checkoutInfo['checkout_id'],
                              amount = ticket.price, 
                              description = checkoutDescription[:127])
    checkout.save()
    # Create the purchase
    purchase = Purchase(owner = user, ticket = ticket, event = event, 
                        price = ticket.price, checkout = checkout)
    purchase.save()
    # If the ticket has a quantity limit
    if ticket.quantity is not None:
        # Schedule the purchase to be expired after some amount of time
        expiration = timezone.now()
        expiration += timedelta(minutes = BBOY_TRANSACTION_EXPIRATION)
        mark_purchase_as_expired.apply_async(args = [purchase], 
                                             eta = expiration)
        # Adjust the ticket quantity
        ticket.quantity = F('quantity') - 1
        ticket.save()
    response = {
        'status':'OK',
        'purchase':serialize_one(purchase),
        'checkout':serialize_one(checkout)
    }
    return json_response(response)