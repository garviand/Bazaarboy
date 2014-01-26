"""
Controller for contact lists
"""

import cgi
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
@validate('POST', ['profile', 'name', 'is_hidden'])
def create(request, params, user):
    """
    Create an empty list
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
    params['name'] = cgi.escape(params['name'])
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'The name must be within 50 characters.'
        }
        return json_response(response)
    lt = List(owner = profile, name = params['name'], 
              is_hidden = params['is_hidden'])
    lt.save()
    response = {
        'status':'OK',
        'list':serialize_one(lt)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], ['name']):
def edit(request, params, user):
    """
    Edit a list
    """
    if not List.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'LIST_NOT_FOUND',
            'message':'The list doesn\'t exist.'
        }
        return json_response(response)
    lt = List.objects.get(id = params['id'])
    profile = lt.owner
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the list.'
        }
        return json_response(response)
    if params['name'] is not None:
        params['name'] = cgi.escape(params['name'])
        if len(params['name']) > 50:
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'The name must be within 50 characters.'
            }
            return json_response(response)
        else:
            lt.name = params['name']
    lt.save()
    response = {
        'status':'OK',
        'list':serialize_one(lt)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'first_name', 'last_name', 'email'])
def add_item(request, params, user):
    """
    Add an item to a list
    """
    if not List.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'LIST_NOT_FOUND',
            'message':'The list doesn\'t exist.'
        }
        return json_response(response)
    lt = List.objects.get(id = params['id'])
    profile = lt.owner
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the list.'
        }
        return json_response(response)
    # Check email format
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    # Check if the name is valid
    if (not REGEX_NAME.match(params['first_name']) or 
        not REGEX_NAME.match(params['last_name'])):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'First or last name contain illegal characters.'
        }
        return json_response(response)
    if len(params['first_name']) > 50 or len(params['last_name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'First or last name is too long.'
        }
        return json_response(response)
    item, created = List_item.objects.get_or_create(_list = lt, 
                                                    email = params['email'])
    item.first_name = params['first_name']
    item.last_name = params['last_name']
    item.save()
    response = {
        'status':'OK',
        'list':serialize_one(lt),
        'item':serialize_one(item)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'event'])
def add_from_event(request, params, user):
    """
    Add items from an event
    """
    if not List.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'LIST_NOT_FOUND',
            'message':'The list doesn\'t exist.'
        }
        return json_response(response)
    lt = List.objects.get(id = params['id'])
    profile = lt.owner
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the list.'
        }
        return json_response(response)
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    purchases = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__isnull = False, 
                                          checkout__is_charged = True), 
                                        event = event, 
                                        is_expired = False) \
                                .prefetch_related('owner')
    for purchase in purchase:
        item, created = List_item.objects \
                                 .get_or_create(_list = lt, 
                                                email = purchase.owner.email)
        item.first_name = purchase.owner.first_name
        item.last_name = purchase.owner.last_name
        item.save()
    response = {
        'status':'OK',
        'list':serialize_one(lt)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'csv', 'format'])
def add_from_csv(request, params, user):
    """
    Add items from a csv file
    """
    pass

@login_required()
@validate('POST', ['id', 'email']):
def remove_item(request, params, user):
    pass

@login_required()
@validate('POST', ['id']):
def delete(request, params, user):
    pass