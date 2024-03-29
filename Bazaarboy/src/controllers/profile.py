"""
Controller for Profile
"""

import cgi
import re
from django.http import Http404
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Count
from django.utils import timezone as tz
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.regex import REGEX_EMAIL, REGEX_URL, REGEX_EIN
from src.serializer import serialize, serialize_one
from src.email import sendProfileMessageEmail, sendNewAccountEmail

import pdb

@login_check()
def index(request, id, user):
    """
    Profile page
    """
    if not Profile.objects.filter(id = id).exists():
        raise Http404
    profile = Profile.objects.select_related().get(id = id)
    pids = [profile.id]
    manager = None
    if Profile_manager.objects.filter(user = user, profile = profile).exists():
        manager = Profile_manager.objects.get(user = user, profile = profile)
    currentEvents = Event.objects.filter(Q(end_time = None, 
                                           start_time__gt = tz.now()) | 
                                         Q(end_time__isnull = False, 
                                           end_time__gt = tz.now()),   
                                         is_launched = True, 
                                         organizers__in = pids) \
                                 .order_by('start_time')
    pastEvents = Event.objects.filter(Q(end_time = None, 
                                        start_time__lt = tz.now()) | 
                                      Q(end_time__isnull = False, 
                                        end_time__lt = tz.now()), 
                                      is_launched = True, 
                                      organizers__in = pids) \
                              .order_by('-start_time')
    return render(request, 'profile/index.html', locals())

@login_required()
def new(request, user):
    """
    Create profile page
    """
    profiles = Profile.objects.filter(managers = user)
    if len(profiles) > 0:
        return redirect('user:settings')
    stripeConnectUrl = r'%s?response_type=code&client_id=%s&scope=%s'
    stripeConnectUrl = stripeConnectUrl % (STRIPE_CONNECT_URL, 
                                           STRIPE_CLIENT_ID, 
                                           STRIPE_SCOPE)
    categories = BBOY_PROFILE_CATEGORIES
    return render(request, 'profile/new.html', locals())

@login_required()
@validate('GET', ['id'])
def profile(request, params, user):
    """
    Return serialized profile data
    """
    if not Profile.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['id'])
    response = {
        'status':'OK',
        'profile':serialize_one(profile)
    }
    return json_response(response)

@validate('GET', ['keyword'])
def search(request, params):
    """
    Search profiles by keyword
    """
    profiles = Profile.objects.filter(name__icontains = params['keyword'])
    results = []
    for profile in profiles:
        profileObj = serialize_one(profile)
        if profile.image:
            profileObj['image_url'] = profile.image.source.url
        else:
            profileObj['image_url'] = None
        results.append(profileObj)
    response = {
        'status':'OK',
        'profiles':results
    }
    return json_response(response)

@login_required()
@validate('POST', ['name', 'description'], 
          ['image', 'location', 'latitude', 'longitude', 'email', 'phone', 
           'link_website', 'link_facebook', 'EIN', 'is_non_profit', 'payment'])
def create(request, params, user):
    """
    Create a profile and set the creating user as the creator
    """
    # Check if the name is valid
    params['name'] = cgi.escape(params['name'])
    if len(params['name']) > 100:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Profile name cannot be over 100 characters.'
        }
        return json_response(response)
    # Create profile object
    params['description'] = cgi.escape(params['description'])
    profile = Profile(name = params['name'], 
                      description = params['description'])
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
            image.is_archived = True
            image.save()
            profile.image = image
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
            profile.location = params['location']
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
            # Valid coordinates, set to profile
            profile.latitude = float(params['latitude'])
            profile.longitude = float(params['longitude'])
    if params['email'] is not None:
        # Check email format
        if not REGEX_EMAIL.match(params['email']):
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL',
                'message':'Email format is invalid.'
            }
            return json_response(response)
        else:
            profile.email = params['email']
    if params['phone'] is not None:
        params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
        if len(params['phone']) != 10:
            response = {
                'status':'FAIL',
                'error':'INVALID_PHONE',
                'message':'The phone number is invalid.'
            }
            return json_response(response)
        else:
            profile.phone = params['phone']
    if params['link_website'] is not None:
        if ((len(params['link_website']) != 0) and 
            not REGEX_URL.match(params['link_website'])):
            response = {
                'status':'FAIL',
                'error':'INVALID_LINK_WEB',
                'message':'Your website link is invalid.'
            }
            return json_response(response)
        else:
            profile.link_website = params['link_website']
    if params['link_facebook'] is not None:
        if ((len(params['link_facebook']) != 0) and 
            not REGEX_URL.match(params['link_facebook'])):
            response = {
                'status':'FAIL',
                'error':'INVALID_LINK_FB',
                'message':'Your facebook link is invalid.'
            }
            return json_response(response)
        else:
            profile.link_facebook = params['link_facebook']
    # Check if is declared as non-profit
    if params['EIN'] is not None:
        if not REGEX_EIN.match(params['EIN']):
            response = {
                'status':'FAIL',
                'error':'INVALID_EIN',
                'message':'The EIN is not in correct format (NN-NNNNNNN).'
            }
            return json_response(response)
        else:
            profile.EIN = params['EIN']
    if params['is_non_profit'] is not None:
        if params['is_non_profit'] and profile.EIN == '':
            response = {
                'status':'FAIL',
                'error':'MISSING_EIN',
                'message':'You need an EIN to prove non-profit status.'
            }
            return json_response(response)
        profile.is_non_profit = params['is_non_profit']
    # Check if payment account is valid
    if params['payment'] is not None:
        if not Payment_account.objects.filter(id = params['payment']).exists():
            response = {
                'status':'FAIL',
                'error':'PAYMENT_ACCOUNT_NOT_FOUND',
                'message':'The payment account doesn\'t exist.'
            }
            return json_response(response)
        paymentAccount = Payment_account.objects.get(id = params['payment'])
        if paymentAccount.owner.id != user.id:
            response = {
                'status':'FAIL',
                'error':'PAYMENT_ACCOUNT_PERMISSION_DENIED',
                'nmessage':'You don\'t have permission for this account.'
            }
            return json_response(response)
        else:
            profile.payment_account = paymentAccount
    # Save profile and establish manager role
    profile.save()
    profileManager = Profile_manager(user = user,
                                     profile = profile,
                                     is_creator = True)
    profileManager.save()
    sendNewAccountEmail(profile)
    response = {
        'status':'OK',
        'profile':serialize_one(profile)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'email', 'phone', 'link_website', 'link_facebook', 'EIN', 'is_non_profit', 'image', 'cover', 'location', 'latitude', 
           'longitude', 'payment'])
def edit(request, params, user):
    """
    Edit an existing profile
    """
    # Check if the profile is valid
    if not Profile.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['id'])
    # Check if the user has permission for the profile
    if not Profile_manager.objects.filter(user = user, profile = profile) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the profile.'
        }
        return json_response(response)
    # Go through all the params and edit the profile accordingly
    if params['name'] is not None:
        params['name'] = cgi.escape(params['name'])
        if not (0 < len(params['name']) <= 100):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Profile name cannot be blank or over 100 characters.'
            }
            return json_response(response)
        else:
            profile.name = params['name']
    if params['description'] is not None:
        params['description'] = cgi.escape(params['description'])
        profile.description = params['description']
    if params['image'] is not None:
        if params['image'].lower() == 'delete':
            if profile.image is not None:
                oldImage = Image.objects.get(id = profile.image.id)
                oldImage.delete()
                profile.image = None
        elif not Image.objects.filter(id = params['image']).exists():
            response = {
                'status':'FAIL',
                'error':'IMAGE_NOT_FOUND',
                'message':'The image doesn\'t exist.'
            }
            return json_response(response)
        else:
            image = Image.objects.get(id = params['image'])
            if profile.image is not None:
                oldImage = Image.objects.get(id = profile.image.id)
                oldImage.delete()
            image.is_archived = True
            image.save()
            profile.image = image
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
            profile.location = params['location']
    if params['latitude'] is not None and params['longitude'] is not None: 
        if (params['latitude'].lower() == 'none' or 
            params['longitude'].lower() == 'none'):
            profile.latitude = None
            profile.longitude = None
        elif not (-90.0 <= float(params['latitude']) <= 90.0 and 
                -180.0 <= float(params['longitude']) <= 180.0):
            response = {
                'status':'FAIL',
                'error':'INVALID_COORDINATES',
                'message':'Latitude/longitude combination is invalid.'
            }
            return json_response(response)
        else:
            profile.latitude = float(params['latitude'])
            profile.longitude = float(params['longitude'])
    if params['email'] is not None:
        # Check email format
        if not REGEX_EMAIL.match(params['email']) and len(params['email']) > 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL',
                'message':'Email format is invalid.'
            }
            return json_response(response)
        else:
            profile.email = params['email']
    if params['phone'] is not None:
        params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
        if len(params['phone']) == 0:
            profile.phone = None
        elif len(params['phone']) != 10:
            response = {
                'status':'FAIL',
                'error':'INVALID_PHONE',
                'message':'The phone number is invalid.'
            }
            return json_response(response)
        else:
            profile.phone = params['phone']
    if params['link_website'] is not None:
        if len(params['link_website']) == 0:
            profile.link_website = None
        if ((len(params['link_website']) != 0) and 
            not REGEX_URL.match(params['link_website'])):
            response = {
                'status':'FAIL',
                'error':'INVALID_LINK_WEB',
                'message':'Your website link is invalid.'
            }
            return json_response(response)
        else:
            profile.link_website = params['link_website']
    if params['link_facebook'] is not None:
        if len(params['link_facebook']) == 0:
            profile.link_facebook = None
        if ((len(params['link_facebook']) != 0) and 
            not REGEX_URL.match(params['link_facebook'])):
            response = {
                'status':'FAIL',
                'error':'INVALID_LINK_FB',
                'message':'Your facebook link is invalid.'
            }
            return json_response(response)
        else:
            profile.link_facebook = params['link_facebook']
    if params['EIN'] is not None:
        if params['EIN'] == '':
            profile.EIN = None
        elif not REGEX_EIN.match(params['EIN']):
            response = {
                'status':'FAIL',
                'error':'INVALID_EIN',
                'message':'The EIN is not in correct format (NN-NNNNNNN).'
            }
            return json_response(response)
        else:
            profile.EIN = params['EIN']
    if params['is_non_profit'] is not None:
        if params['is_non_profit'] and profile.EIN == '':
            response = {
                'status':'FAIL',
                'error':'MISSING_EIN',
                'message':'You need an EIN to prove non-profit status.'
            }
            return json_response(response)
        profile.is_non_profit = params['is_non_profit']
    if params['payment'] is not None:
        if not Payment_account.objects.filter(id = params['payment']).exists():
            response = {
                'status':'FAIL',
                'error':'PAYMENT_ACCOUNT_NOT_FOUND',
                'message':'The payment account doesn\'t exist.'
            }
            return json_response(response)
        paymentAccount = Payment_account.objects.get(id = params['payment'])
        if paymentAccount.owner.id != user.id:
            response = {
                'status':'FAIL',
                'error':'PAYMENT_ACCOUNT_PERMISSION_DENIED',
                'nmessage':'You don\'t have permission for this account.'
            }
            return json_response(response)
        else:
            profile.payment_account = paymentAccount
    # Save the changes
    profile.save()
    response = {
        'status':'OK',
        'profile':serialize_one(profile)
    }
    return json_response(response)

@login_required()
@validate('POST', ['profile', 'user'])
def create_manager(request, params, user):
    """
    Make a user the manager of a profile
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
    # Check if the specified user is valid
    if not User.objects.filter(id = params['user']).exists():
        response = {
            'status':'FAIL',
            'error':'USER_NOT_FOUND',
            'message':'The user doesn\'t exist.'
        }
        return json_response(response)
    manager = User.objects.get(id = params['user'])
    # Check if the logged-in user is the creator of the profile
    if not Profile_manager.objects.filter(user = user, profile = profile, 
                                          is_creator = True).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_CREATOR',
            'message':'Only the creator of the profile can create managers.'
        }
        return json_response(response)
    # Make the specified user the manager
    profileManager = Profile_manager(user = manager, profile = profile)
    profileManager.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['profile'], ['user'])
def delete_manager(request, params):
    """
    Remove a user from the managers of a profile
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
    # Check if a user is specified
    if params['user'] is not None:
        # If so, treat it as a creator's attempt to delete a manager
        # Check if the logged-in user is the creator of the profile
        if not Profile_manager.objects.filter(user = user, profile = profile, 
                                              is_creator = True).exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_CREATOR',
                'message':'Only the creator can delete managers.'
            }
            return json_response(response)
        # Check if the specified user exists
        if not User.objects.filter(id = params['user']).exists():
            response = {
                'status':'FAIL',
                'error':'USER_NOT_FOUND',
                'message':'The user doesn\'t exist.'
            }
            return json_response(response)
        manager = User.objects.get(id = params['user'])
        # Check if the specified user is a manager
        if not Profile_manager.objects.filter(user = manager, 
                                              profile = profile).exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'The user is not a manager of the profile.'
            }
            return json_response(response)
        profileManager = Profile_manager.objects.get(user = manager, 
                                                     profile = profile)
        # Check if the specified user is the creator
        if user.id == manager.id:
            response = {
                'status':'FAIL',
                'error':'IS_CREATOR',
                'message':'You cannot be removed from the profile you created.'
            }
            return json_response(response)
        # Remove the user from the managers
        profileManager.delete()
        response = {
            'status':'OK'
        }
        return json_response(response)
    else:
        # If not, treat it as a manager's attempt to delete itself from 
        # the profile
        # Check if the user is a manager
        if not Profile_manager.objects.filter(user = user, profile = profile) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You are not a manager of the profile.'
            }
            return json_response(response)
        profileManager = Profile_manager.objects.get(user = user, 
                                                     profile = profile)
        # Check if the user is the creator of the profile
        if profileManager.is_creator:
            response = {
                'status':'FAIL',
                'error':'IS_CREATOR',
                'message':'You cannot be removed from the profile you created.'
            }
            return json_response(response)
        # Remove the user from the managers
        profileManager.delete()
        response = {
            'status':'OK'
        }
        return json_response(response)

@validate('POST', ['name', 'useremail', 'message', 'profile', 'event'])
def message(request, params):
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    if not REGEX_EMAIL.match(params['useremail']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    event = Event.objects.get(id = params['event'])
    sendProfileMessageEmail(params['name'], params['useremail'], params['message'], profile, event)
    response = {
                'status':'OK'
    }
    return json_response(response)