"""
Controller for fundraisers
"""

from datetime import datetime
from django.http import Http404
from django.utils import timezone
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_check()
def index(request, id, loggedIn):
    """
    Fundraiser event page
    """
    if not Fundraiser.objects.filter(id = id).exists():
        return Http404
    fundraiser = Fundraiser.objects.get(id = id)
    return render(request, 'fundraiser.html', locals())

@login_required()
@validate('GET', ['id'])
def fundraiser(request, params):
    """
    Return serialized data for the fundraiser
    """
    if not Fundraiser.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'FUNDRAISER_NOT_FOUND',
            'message':'The fundraiser doesn\'t exist.'
        }
        return json_response(response)
    fundraiser = Fundraiser.objects.get(id = params['id'])
    response = {
        'status':'OK',
        'fundraiser':serialize_one(fundraiser)
    }
    return json_response(response)

@login_required()
@validate('POST', 
          ['profile', 'name', 'description', 'location', 'category', 
           'deadline'], 
          ['latitude', 'longitude', 'is_private'])
def create(request, params):
    """
    Create a new fundraiser
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
    # Check the deadline
    params['deadline'] = datetime.strptime(params['deadline'], FORMAT_DATETIME)
    if params['deadline'] < timezone.now():
        response = {
            'status':'FAIL',
            'error':'INVALID_DEADLINE',
            'message':'The deadline is invalid.'
        }
        return json_response(response)
    # Checks passed, create the model
    fundraiser = Fundraiser(name = params['name'], 
                            description = params['description'], 
                            location = params['location'], 
                            category = params['category'], 
                            owner = profile, 
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
            # Valid coordinates, set to fundraiser
            fundraiser.latitude = float(params['latitude'])
            fundraiser.longitude = float(params['longitude'])
    # Check if it's a private fundraiser
    if params['is_private'] is not None:
        fundraiser.is_private = params['is_private']
    # Save to database
    fundraiser.save()
    response = {
        'status':'OK',
        'fundraiser':serialize_one(fundraiser)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def edit(request, params):
    """
    Edit an existing fundraiser
    """
    # Check if the fundraiser is valid
    if not Fundraiser.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'FUNDRAISER_NOT_FOUND',
            'message':'The fundraiser doesn\'t exist.'
        }
        return json_response(response)
    fundraiser = Fundraiser.objects.get(id = params['id'])
    # Check if user has permission for the fundraiser
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, 
                                          profile = fundraiser.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the fundraiser.'
        }
        return json_response(response)
    # Go through all params and edit the fundraiser accordingly
    if params['deadline'] is not None:
        if fundraiser.is_launched:
            response = {
                'status':'FAIL',
                'error':'LAUNCHED_FUNDRAISER',
                'message':'You can\'t change the deadline while launched.'
            }
            return json_response(response)
        params['deadline'] = datetime.strptime(params['deadline'], 
                                               FORMAT_DATETIME)
        if params['deadline'] < timezone.now():
            response = {
                'status':'FAIL',
                'error':'INVALID_DEADLINE',
                'message':'The deadline is invalid.'
            }
        else:
            fundraiser.deadline = params['deadline']
    if params['name'] is not None:
        if len(params['name']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_NAME',
                'message':'Name cannot be blank.'
            }
            return json_response(response)
        else:
            fundraiser.name = params['name']
    if params['description'] is not None:
        if len(params['description']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_DESCRIPTION',
                'message':'Description cannot be blank.'
            }
            return json_response(response)
        else:
            fundraiser.description = params['description']
    if params['location'] is not None:
        if len(params['location']) == 0:
            response = {
                'status':'FAIL',
                'error':'BLANK_LOCATION',
                'message':'Location cannot be blank.'
            }
            return json_response(response)
        else:
            fundraiser.location = params['location']
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
            fundraiser.latitude = float(params['latitude'])
            fundraiser.longitude = float(params['longitude'])
    if params['category'] is not None:
        fundraiser.category = params['category']
    if params['is_private'] is not None:
        fundraiser.is_private = params['is_private']
    # Save the changes
    fundraiser.save()
    response = {
        'status':'OK',
        'fundraiser':serialize_one(fundraiser)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def launch(request, params):
    """
    Launch a fundraiser
    """
    # Check if the fundraiser is valid
    if not Fundraiser.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'FUNDRAISER_NOT_FOUND',
            'message':'The fundraiser doesn\'t exist.'
        }
        return json_response(response)
    fundraiser = Fundraiser.objects.get(id = params['id'])
    # Check if user has permission for the fundraiser
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, 
                                          profile = fundraiser.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the fundraiser.'
        }
        return json_response(response)
    # Check if the deadline is valid
    if fundraiser.deadline < timezone.now():
        response = {
            'status':'FAIL',
            'error':'INVALID_DEADLINE',
            'message':'The deadline is invalid.'
        }
        return json_response(response)
    # Launch the fundraiser
    fundraiser.is_launched = True
    fundraiser.save()
    response = {
        'status':'OK',
        'fundraiser':serialize_one(fundraiser)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delaunch(request, params):
    """
    Take a fundraiser offline
    """
    # Check if the fundraiser is valid
    if not Fundraiser.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'FUNDRAISER_NOT_FOUND',
            'message':'The fundraiser doesn\'t exist.'
        }
        return json_response(response)
    fundraiser = Fundraiser.objects.get(id = params['id'])
    # Check if user has permission for the fundraiser
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, 
                                          profile = fundraiser.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the fundraiser.'
        }
        return json_response(response)
    # Check if the fundraiser is launched
    if not fundraiser.is_launched:
        response = {
            'status':'FAIL',
            'error':'NOT_LAUNCHED',
            'message':'The fundraiser is not yet launched.'
        }
        return json_response(response)
    # Check if the deadline has reached
    if fundraiser.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'DEADLINE_PAST_DUE',
            'message':'The deadline has passed.'
        }
        return json_response(response)
    # Refund all the donations
    donations = Donation.objects.filter(fundraiser = fundraiser)
    for donation in donations:
        pass
    # Mark the fundraiser as offline
    fundraiser.is_launched = False
    fundraiser.save()
    response = {
        'status':'OK',
        'fundraiser':serialize_one(fundraiser)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete(request, params):
    """
    Delete a fundraiser
    """
    # Check if the fundraiser is valid
    if not Fundraiser.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'FUNDRAISER_NOT_FOUND',
            'message':'The fundraiser doesn\'t exist.'
        }
        return json_response(response)
    fundraiser = Fundraiser.objects.get(id = params['id'])
    # Check if user has permission for the fundraiser
    user = User.objects.get(id = request.session['user'])
    if not Profile_manager.objects.filter(user = user, 
                                          profile = fundraiser.owner) \
                                  .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the fundraiser.'
        }
        return json_response(response)
    # Check if the fundraiser is launched
    if fundraiser.is_launched:
        response = {
            'status':'FAIL',
            'error':'LAUNCHED_FUNDRAISER',
            'message':'The fundraiser is launched, please take it offline first.'
        }
        return json_response(response)
    # Delete the fundraiser
    fundraiser.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate()
def donate(request, params):
    pass