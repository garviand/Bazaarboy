"""
Controller for initiative events
"""

from datetime import datetime, timedelta
from django.http import Http404
from django.utils import timezone
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

FORMAT_DATETIME = '%Y-%m-%d %X'

@login_check()
def index(request, id, loggedIn):
    """
    Initiative event page
    """
    if not Initiative.objects.filter(id = id).exists():
        return Http404
    initiative = Initiative.objects.get(id = id)
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
          ['profile', 'name', 'description', 'location', 'category', 'goal', 
           'deadline'], 
          ['latitude', 'longitude', 'is_private'])
def create(request, params):
    """
    Create a new initiative event
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
    # Check the goal
    params['goal'] = float(params['goal'])
    if params['goal'] < 20.0:
        response = {
            'status':'FAIL',
            'error':'INVALID_GOAL',
            'message':'The initiative goal is too small.'
        }
    # Check the deadline
    params['deadline'] = datetime.strptime(params['deadline'], FORMAT_DATETIME)
    if params['deadline'] < timezone.now():
        response = {
            'status':'FAIL',
            'error':'INVALID_DEADLINE',
            'message':'The deadline is invalid.'
        }
    # Validated, create the model
    initiative = Initiative(name = params['name'], 
                            description = params['description'], 
                            location = params['location'], 
                            category = params['category'], 
                            owner = profile, 
                            goal = params['goal'], 
                            deadline = params['deadline'])
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
            # Valid coordinates, set to initiative
            initiative.latitude = float(params['latitude'])
            initiative.longitude = float(params['longitude'])
    # Check if it's a private initiative
    if params['is_private'] is not None:
        initiative.is_private = params['is_private']
    # Save to database
    initiative.save()
    response = {
        'status':'OK',
        'event':serialize_one(initiative)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'location', 'latitude', 'longitude', 
           'category', 'is_private', 'goal', 'deadline'])
def edit(request, params):
    """
    Edit an existing initiative
    """
    # Check if the initiative is valid
    if not Initiative.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'INITIATIVE_NOT_FOUND',
            'message':'The initiative doesn\'t exist.'
        }
        return json_response(response)
    initiative = Initiative.objects.get(id = params['id'])
    # Check if user has permission for the initiative
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, 
                                          profile = initiative.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the initiative.'
        }
        return json_response(response)
    # Go through all params and edit the initiative accordingly
    if params['goal'] is not None:
        if initiative.is_launched:
            response = {
                'status':'FAIL',
                'error':'LAUNCHED_INITIATIVE',
                'message':'You can\'t change the goal while launched.'
            }
            return json_response(response)
        params['goal'] = float(params['goal'])
        if params['goal'] < 20.0:
            response = {
                'status':'FAIL',
                'error':'INVALID_GOAL',
                'message':'The goal is too small.'
            }
        else:
            initiative.goal = params['goal']
    if params['deadline'] is not None:
        if initiative.is_launched:
            response = {
                'status':'FAIL',
                'error':'LAUNCHED_INITIATIVE',
                'message':'You can\'t change the deadline while launched.'
            }
            return json_response(response)
        params['deadline'] = datetime.strptime(params['deadline'], 
                                               FORMAT_DATETIME)
        if params['deadline'] < timezone.now():
            response = {
                'status':'FAIL',
                'error':'INVALID_DEADLINE',
                'message':'The deadline is too small.'
            }
        else:
            initiative.deadline = params['deadline']
    if params['name'] is not None:
        if len(params['name']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_NAME',
                'message':'Name cannot be blank.'
            }
            return json_response(response)
        else:
            initiative.name = params['name']
    if params['description'] is not None:
        if len(params['description']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_DESCRIPTION',
                'message':'Description cannot be blank.'
            }
            return json_response(response)
        else:
            initiative.description = params['description']
    if params['location'] is not None:
        if len(params['location']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_LOCATION',
                'message':'Location cannot be blank.'
            }
            return json_response(response)
        else:
            initiative.location = params['location']
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
            initiative.latitude = float(params['latitude'])
            initiative.longitude = float(params['longitude'])
    if params['category'] is not None:
        initiative.category = params['category']
    if params['is_private'] is not None:
        initiative.is_private = params['is_private']
    response = {
        'status':'OK',
        'initiative':serialize_one(initiative)
    }
    return json_response(response)

@login_required()
@validate()
def launch(request, params):
    pass

@login_required()
@validate()
def delaunch(request, params):
    pass

@login_required()
@validate()
def delete(request, params):
    pass

@login_required()
@validate('POST', ['initiative', 'name', 'description', 'price'], ['quantity'])
def create_reward(request, params):
    """
    Create a reward for the initiative
    """
    # Check if initiative is valid
    if not Initiative.objects.filter(id = params['initiative']):
        response = {
            'status':'FAIL',
            'error':'INVALID_INITIATIVE',
            'message':'The initiative doesn\'t exist.'
        }
        return json_response(response)
    initiative = Initiative.objects.get(id = params['initiative'])
    # Check if user has permission for the initiative
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, 
                                          profile = initiative.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the initiative.'
        }
        return json_response(response)
    # Check if the initiative has passed its deadline
    if initiative.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'PAST_INITIATIVE',
            'message':'You cannot add a reward to a past initiative.'
        }
        return json_response(response)
    # Check the price
    params['price'] = float(params['price'])
    if params['price'] <= 0:
        response = {
            'status':'FAIL',
            'error':'INVALID_PRICE',
            'message':'The price is invalid.'
        }
        return json_response(response)
    reward = Reward(initiative = initiative, 
                    name = params['name'], 
                    description = params['description'], 
                    price = params['price'])
    # Check the quantity
    if params['quantity'] is not None:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'The quantity is invalid.'
            }
            return json_response(response)
        else:
            reward.quantity = params['quantity']
    # All checks passed, write to database
    reward.save()
    response = {
        'status':'OK',
        'reward':serialize_one(reward)
    }
    return json_response(response)

@login_required()
@validate()
def edit_reward(request, params):
    pass

@login_required()
@validate()
def delete_reward(request, params):
    pass

@login_required()
@validate()
def pledge(request, params):
    pass