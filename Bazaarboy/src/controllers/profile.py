"""
Controller for Profile
"""

from django.http import Http404
from django.shortcuts import render
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_check()
def index(request, id, loggedIn):
    """
    Profile page
    """
    if not Profile.objects.filter(id = id).exists():
        raise Http404
    profile = Profile.objects.get(id = id)
    return render(request, 'profile.html', locals())

@login_required()
@validate('GET', ['id'])
def profile(request, params):
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

@login_required()
@validate('POST', 
          ['name', 'description', 'community', 'category'], 
          ['latitude', 'longitude', 'wepay'])
def create(request, params):
    """
    Create a profile and set the creating user as the creator
    """
    # Check if the name is too long
    if len(params['name']) > 100:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Profile name cannot be over 100 characters.'
        }
        return json_response(response)
    # Check if community exists
    if not Community.objects.filter(id = params['community']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist'
        }
        return json_response(response)
    # Create profile object
    community = Community.objects.get(id = params['community'])
    profile = Profile(name = params['name'], 
                      description = params['description'], 
                      community = community, 
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
            # Valid coordinates, set to profile
            profile.latitude = float(params['latitude'])
            profile.longitude = float(params['longitude'])
    # Check WePay account
    user = User.objects.get(id = request.session['user'])
    if params['wepay'] is not None:
        if not Wepay_account.objects.filter(id = params['wepay']):
            response = {
                'status':'FAIL',
                'error':'INVALID_WEPAY',
                'message':'The wepay account is invalid.'
            }
            return json_response(response)
        wepayAccount = Wepay_account.objects.get(id = params['wepay'])
        if user != wepayAccount.owner:
            response = {
                'status':'FAIL',
                'error':'NOT_WEPAY_OWNER',
                'message':'You don\'t have permission for this WePay account.'
            }
            return json_response(response)
        profile.wepay_account = wepayAccount
    # Save profile and establish manager role
    profile.save()
    profileManager = Profile_manager(user = user,
                                     profile = profile,
                                     is_creator = True)
    profileManager.save()
    response = {
        'status':'OK',
        'profile':serialize_one(profile)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'category', 'latitude', 'longitude', 
           'wepay'])
def edit(request, params):
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
    user = User.objects.get(id = request.session['user'])
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
        profile.description = params['description']
    if params['category'] is not None:
        profile.category = params['category']
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
            profile.latitude = float(params['latitude'])
            profile.longitude = float(params['longitude'])
    # Save the changes
    profile.save()
    response = {
        'status':'OK',
        'profile':serialize_one(profile)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete(request, params):
    pass