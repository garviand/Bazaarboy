"""
Controller for contact lists
"""

import cgi
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one
from src.regex import REGEX_EMAIL, REGEX_NAME, REGEX_SLUG
from django.shortcuts import render, redirect
from django.db.models import F, Q, Count
import csv

import pdb

@login_required()
def index(request, user):
    """
    List Dashboard
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    lists = List.objects.filter(owner = profile, is_deleted = False)
    listsCount = lists.count()
    for lt in lists:
        list_items = List_item.objects.filter(_list = lt)
        lt.items = list_items.count()
    return render(request, 'list/index.html', locals())

@login_required()
def list(request, lt, user):
    """
    Single List Page
    """
    if not List.objects.filter(id = lt, is_deleted = False).exists():
        return redirect('list:index')
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    if List.objects.filter(id = lt).exists():
        lt = List.objects.get(id = lt)
        if not Profile_manager.objects.filter(profile = lt.owner, user = user).exists():
            return redirect('index:index')
        list_items = List_item.objects.filter(_list = lt).order_by('-id')
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
    else:
        return redirect('index:index')
    if not Profile_manager.objects.filter(profile = lt.owner, user = user).exists():
        return redirect('index:index')
    return render(request, 'list/list.html', locals())
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
@validate('POST', ['id'], ['name'])
def edit(request, params, user):
    """
    Edit a list
    """
    if not List.objects.filter(id = params['id'], is_deleted = False).exists():
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
@validate('POST', ['id'])
def remove_item(request, params, user):
    """
    Remove an item from a list
    """
    if not List_item.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'LIST_ITEM_NOT_FOUND',
            'message':'The list item doesn\'t exist.'
        }
        return json_response(response)
    item = List_item.objects.get(id = params['id'])
    lt = item._list
    profile = lt.owner
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the list.'
        }
        return json_response(response)
    item.delete()
    response = {
            'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'first_name', 'last_name', 'email'], ['note'])
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
    if params['note']:
        item.note = params['note']
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
    if not List.objects.filter(id = params['id'], is_deleted = False).exists():
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
    added = 0
    duplicates = 0
    for purchase in purchases:
        if not List_item.objects.filter(_list = lt, email = purchase.owner.email).exists():
            item = List_item(_list = lt, email = purchase.owner.email, first_name = purchase.owner.first_name, last_name = purchase.owner.last_name)
            item.save()
            added += 1
        else:
            duplicates += 1
    response = {
        'status':'OK',
        'list':serialize_one(lt),
        'added': added,
        'duplicates': duplicates
    }
    return json_response(response)

@login_required()
@validate('POST', ['csv'])
def prepare_csv(request, params, user):
    """
    Prepare CSV For List Upload
    """
    if not Csv.objects.filter(id = params['csv']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    csv_file = Csv.objects.get(id = params['csv'])
    csvfile = csv_file.source.file
    reader = csv.reader(csvfile)
    results = {}
    for num, row in enumerate(reader):
        results[num] = row
    csvfile.close()
    response = {
        'status':'OK',
        'results': results
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'csv', 'format'])
def add_from_csv(request, params, user):
    """
    Add items from a csv file
    """
    if not List.objects.filter(id = params['id'], is_deleted = False).exists():
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
    # Check if CSV Exists
    if not Csv.objects.filter(id = params['csv']).exists():
        response = {
            'status':'FAIL',
            'error':'CSV_NOT_FOUND',
            'message':'The csv doesn\'t exist.'
        }
        return json_response(response)
    csv_file = Csv.objects.get(id = params['csv'])
    csvfile = csv_file.source.file
    reader = csv.reader(csvfile)
    # Load Format {field_type:col}
    format = json.loads(params['format'])
    added = 0
    duplicates = 0
    for num, row in enumerate(reader):
        if 'email' in format and len(row) >= format['email'] and REGEX_EMAIL.match(row[format['email']]):
            if not List_item.objects.filter(_list = lt, email = row[format['email']]).exists():
                item = List_item(_list = lt, email = row[format['email']])
                item.first_name = row[format['first_name']]
                if 'last_name' in format:
                    item.last_name = row[format['last_name']]
                item.save()
                added += 1
            else:
                duplicates += 1

    response = {
        'status':'OK',
        'list':serialize_one(lt),
        'added': added,
        'duplicates': duplicates
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete(request, params, user):
    """
    Delete List
    """
    if not List.objects.filter(id = params['id'], is_deleted = False).exists():
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
    lt.is_deleted = True
    lt.save()
    response = {
        'status': 'OK',
        'list': serialize_one(lt)
    }
    return json_response(response)
