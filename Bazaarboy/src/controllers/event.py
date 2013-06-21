"""
Controller for normal events
"""

from datetime import datetime, timedelta
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from kernel.models import *
from src.controllers.request import validate, login_check, login_required
from src.serializer import serialize_one

@login_check()
def index(request, id, loggedIn):
    """
    Normal event page
    """
    if not Event.objects.filter(id = id).exists():
        return Http404
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
          ['end_time', 'latitude', 'longitude', 'is_private', 'is_launched', 
           'is_repeated'])
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
    if (params['start_time'] < timezone.now() + timedelta(hours = 6) or 
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
        # Valid coordinates, set to profile
        event.latitude = float(params['latitude'])
        event.longitude = float(params['longitude'])
    # Boolean parameters
    if params['is_private'] is not None:
        event.is_private = params['is_private']
    if params['is_launched'] is not None:
        event.is_launched = params['is_launched']
    if params['is_repeated'] is not None:
        event.is_repeated = params['is_repeated']
    # Save to database
    event.save()
    response = {
        'status':'OK',
        'event':serialize_one(event)
    }
    return json_response(response)