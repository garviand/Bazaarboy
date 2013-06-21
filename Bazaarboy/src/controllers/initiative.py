"""
Controller for initiative events
"""

from datetime import datetime, timedelta
from django.http import Http404
from django.utils import timezone
from src.controllers.request import validate, login_check, login_required

FORMAT_DATETIME = '%Y-%m-%d %X'

@login_check()
def index(request, id, loggedIn):
    return render(request, 'initiative.html', locals())

@login_required()
@validate('GET', ['id'])
def initiative(request, params):
    """
    Return serialized data for the initiative event
    """
    if not initiative.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'INITIATIVE_NOT_FOUND',
            'message':'The initiative doesn\'t exist.'   
        }
        return json_response(response)
    initiative = Initiative.objects.get(id = params['id'])
    response = {
        'status':'OK',
        'event':serialize_one(initiative)
    }
    return json_response(response)

@login_required()
@validate('POST', 
          ['profile', 'name', 'description', 'start_time', 'location', 
           'category', 'goal', 'deadline'], 
          ['end_time', 'latitude', 'longitude', 'is_private', 'is_launched'])
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
    # Check the goal
    params['goal'] = float(params['goal'])
    if params['goal'] < 20.0:
        response = {
            'status':'FAIL',
            'error':'INVALID_GOAL',
            'message':'The initiative goal is invalid.'
        }
    # Check the deadline
    params['deadline'] = datetime.strptime(params['deadline'], FORMAT_DATETIME)
    if (params['deadline'] < timezone.now() + timedelta(hours = 6) or 
        params['deadline'] >= params['start_time']):
        response = {
            'status':'FAIL',
            'error':'INVALID_DEADLINE',
            'message':'The deadline is invalid.'
        }
    # Validated, create the model
    initiative = Initiative(name = params['name'], 
                  description = params['description'], 
                  start_time = params['start_time'], 
                  end_time = params['end_time'], 
                  location = params['location'], 
                  category = params['category'], 
                  owner = profile, 
                  goal = params['goal'], 
                  deadline = params['deadline'])
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
        initiative.latitude = float(params['latitude'])
        initiative.longitude = float(params['longitude'])
    # Boolean parameters
    if params['is_private'] is not None:
        initiative.is_private = params['is_private']
    if params['is_launched'] is not None:
        initiative.is_launched = params['is_launched']
    # Save to database
    initiative.save()
    response = {
        'status':'OK',
        'event':serialize_one(initiative)
    }
    return json_response(response)