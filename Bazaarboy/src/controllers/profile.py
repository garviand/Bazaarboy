"""
Controller for Profile
"""

from django.shortcuts import render
from kernel.models import *
from src.serializer import serialize_one
from request import json_response, validate, login_required, login_check

@login_check()
def index(request, id, loggedIn):
    """
    Profile page
    """
    return render(request, 'profile.html', locals())

@login_required()
@validate('POST', 
          ['name', 'description', 'community', 'category'], 
          ['latitude', 'longitude'])
def create(request, params):
    """
    Create a profile and set the creating user as the creator
    """
    # Check name, description, and category
    if not (len(params['name']) <= 100 and 
            len(params['description']) <= 1000 and 
            len(params['category']) <= 30):
        response = {
            'status':'FAIL',
            'error':'INVALID_PARAM',
            'message':'Some parameters are invalid.'
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
                      category = category)
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
        # Valid coordinates, set to profile
        profile.latitude = float(params['latitude'])
        profile.longitude = float(params['longitude'])
    # Save profile and establish manager role
    profile.save()
    user = User.objects.get(id = request.session['user']['id'])
    profileManager = Profile_manager(user = user,
                                     profile = profile,
                                     is_creator = True)
    profileManager.save()
    response = {
        'status':'OK',
        'profile':serialize_one(profile)
    }
    return json_response(response)