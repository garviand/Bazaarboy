"""
Controller for contact lists
"""

import cgi
import ordereddict
import json
import simplejson
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
    active_sign_ups = Sign_up.objects.filter()
    for lt in lists:
        list_items = List_item.objects.filter(_list = lt)
        lt.items = list_items.count()
    return render(request, 'list/index.html', locals())

@login_required()
@validate('GET', [], ['eid'])
def list(request, lt, user, params):
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
    if params['eid'] is not None:
        if Event.objects.filter(id = params['eid']).exists():
            event = Event.objects.get(id = params['eid'])
    rewards = Reward_item.objects.filter(owner = profile, quantity__gt = 0, expiration_time__gte = timezone.now())
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
@validate('POST', ['id', 'email'], ['first_name', 'last_name', 'note'])
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
    item, created = List_item.objects.get_or_create(_list = lt, email = params['email'])
    if params['first_name'] is not None:
        item.first_name = params['first_name']
    if params['last_name'] is not None:
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
            try:
                item.save()
                added += 1
            except Exception, e:
                pass
        else:
            duplicates += 1
    organizer = Organizer.objects.get(event = event, profile__managers = user)
    if Recap.objects.filter(organizer = organizer, is_viewed = False).exists():
        recap = Recap.objects.get(organizer = organizer)
        recap.is_viewed = True
        recap.list_added = True
        recap.save()
    response = {
        'status':'OK',
        'list':serialize_one(lt),
        'added': added,
        'duplicates': duplicates
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'signup'])
def add_from_sign_up(request, params, user):
    """
    Add items from a sign up list
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
    if not Sign_up.objects.filter(id = params['signup'], owner = profile).exists():
        response = {
            'status':'FAIL',
            'error':'SIGNUP_NOT_FOUND',
            'message':'The sign up doesn\'t exist.'
        }
        return json_response(response)
    signup = Sign_up.objects.get(id = params['signup'])
    signup_items = Sign_up_item.objects.filter(sign_up = signup)
    added = 0
    duplicates = 0
    for signup_item in signup_items:
        if not List_item.objects.filter(_list = lt, email = signup_item.email).exists():
            item = List_item(_list = lt, email = signup_item.email, first_name = signup_item.first_name, last_name = signup_item.last_name)
            try:
                item.save()
                added += 1
            except Exception, e:
                pass
        else:
            item = List_item.objects.filter(_list = lt, email = signup_item.email)[0]
            item.first_name = signup_item.first_name
            item.last_name = signup_item.last_name
            item.save()
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
    csv_file.source.file._mode = 'rU'
    csv_file.save()
    csvfile = csv_file.source.file
    reader = csv.reader(csvfile.read().splitlines())
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
    reader = csv.reader(csvfile.read().splitlines())
    # Load Format {field_type:col}
    format = json.loads(params['format'])
    added = 0
    duplicates = 0
    for num, row in enumerate(reader):
        if 'email' in format and len(row) >= format['email'] and REGEX_EMAIL.match(row[format['email']]):
            if not List_item.objects.filter(_list = lt, email = row[format['email']]).exists():
                item = List_item(_list = lt, email = row[format['email']])
                if 'first_name' in format:
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

@login_check()
def sign_up(request, signup, user):
    """
    Sign Up Page
    """
    if not Sign_up.objects.filter(id = signup).exists():
        return redirect('index')
    else:
        signup = Sign_up.objects.get(id = signup)
        extra_fields = []
        if signup.extra_fields:
            custom_fields = simplejson.loads(signup.extra_fields, object_pairs_hook=ordereddict.OrderedDict)
            for field in ordereddict.OrderedDict(sorted(custom_fields.items())).items():
                extra_fields.append(field[1])
    return render(request, 'list/sign-up.html', locals())

@login_required()
def manage_sign_up(request, signup, user):
    if not Sign_up.objects.filter(id = signup).exists():
        response = {
            'status':'FAIL',
            'error':'SIGN_UP_NOT_FOUND',
            'message':'The sign up doesn\'t exist.'
        }
        return json_response(response)
    sign_up = Sign_up.objects.get(id = signup)
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = sign_up.owner, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the sign up.'
        }
        return json_response(response)
    sign_ups = Sign_up_item.objects.filter(sign_up = sign_up).order_by('-created_time')
    for item in sign_ups:
        if not item.assigned:
            item.new = True
            item.assigned = True
            item.save()
        else:
            item.new = False
        try:
            fields = json.loads(item.extra_fields)
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            item.extra_fields = fields
    lists = List.objects.filter(owner = sign_up.owner, is_deleted = False)
    for lt in lists:
        list_items = List_item.objects.filter(_list = lt)
        lt.items = list_items.count()
    rewards = Reward_item.objects.filter(owner = sign_up.owner, quantity__gt = 0, expiration_time__gte = timezone.now())
    return render(request, 'list/manage-sign-up.html', locals())

@login_required()
def new_sign_up(request, user):
    """
    Sign Up Create Page
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    return render(request, 'list/new-sign-up.html', locals())

@login_required()
@validate('POST', ['name', 'description', 'end_time'], ['image', 'extra_fields'])
def create_sign_up(request, params, user):
    """
    Create Sign Up Form
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    params['name'] = cgi.escape(params['name'])
    if not (0 < len(params['name']) <= 100):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Form name cannot be blank or over 100 characters.'
        }
        return json_response(response)
    params['description'] = cgi.escape(params['description'])
    if not (0 < len(params['description']) <= 500):
        response = {
            'status':'FAIL',
            'error':'INVALID_DESCRIPTION',
            'message':'Form description cannot be blank or over 500 characters.'
        }
        return json_response(response)
    if params['end_time'] < timezone.now():
        response = {
            'status':'FAIL',
            'error':'INVALID_END_TIME',
            'message':'The Sign Up End Time Must Be After Today'
        }
        return json_response(response)
    sign_up = Sign_up(owner = profile, name = params['name'], description = params['description'], end_time = params['end_time'])
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
            sign_up.extra_fields = json.dumps(fields)
    if params['image'] is not None:
        if not Image.objects.filter(id = params['image']).exists():
            response = {
                'status':'FAIL',
                'error':'IMAGE_NOT_FOUND',
                'message':'The image doesn\'t exist.'
            }
            return json_response(response)
        else:
            image = Image.objects.get(id = params['image'])
            sign_up.image = image
    sign_up.save()
    response = {
        'status':'OK',
        'sign_up': serialize_one(sign_up)
    }
    return json_response(response)

@validate('POST', ['first_name', 'last_name', 'email', 'sign_up'], ['extra_fields'])
def submit_sign_up(request, params):
    """
    Submit Sign Up Form
    """
    if not Sign_up.objects.filter(id = params['sign_up']).exists():
        response = {
            'status':'FAIL',
            'error':'INVALID_FORM',
            'message':'The Sign Up form does not exist'
        }
        return json_response(response)
    sign_up = Sign_up.objects.get(id = params['sign_up'])
    if sign_up.end_time is not None and sign_up.end_time < timezone.now():
        response = {
            'status':'FAIL',
            'error':'FORM_ENDED',
            'message':'The sign up form is no longer active.'
        }
        return json_response(response)
    params['first_name'] = cgi.escape(params['first_name'])
    if not (0 < len(params['first_name']) <= 100):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'First Name cannot be blank or over 100 characters.'
        }
        return json_response(response)
    params['last_name'] = cgi.escape(params['last_name'])
    if not (0 < len(params['last_name']) <= 100):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Last Name cannot be blank or over 100 characters.'
        }
        return json_response(response)
    sign_up_item = Sign_up_item(sign_up = sign_up, first_name = params['first_name'], last_name = params['last_name'], email = params['email'])
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
            sign_up_item.extra_fields = json.dumps(fields)
    sign_up_item.save()
    response = {
        'status':'OK',
        'sign_up_item': serialize_one(sign_up_item)
    }
    return json_response(response)