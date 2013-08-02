"""
Controller for city
"""

from django.db.models import Q
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
def index(request, id, user):
    pass

@admin_required()
@validate('GET', ['id'])
def city(request, params, admin):
    """
    Returns the serialized data about a city
    """
    if not City.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city doesn\'t exist.'
        }
        return json_response(response)
    city = City.objects.get(id = params['id'])
    response = {
        'status':'OK',
        'city':serialize_one(city)
    }
    return json_response(response)

@admin_required()
@validate('POST', ['name', 'state', 'latitude', 'longitude'])
def create(request, params, admin):
    """
    Create a new city
    """
    # Check if the name is too long
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'The name cannot be over 50 characters.'
        }
        return json_response(response)
    # Check if the state is valid
    params['state'] = params['state'].upper()
    if not params['state'] in BBOY_STATES:
        response = {
            'status':'FAIL',
            'error':'INVALID_STATE',
            'message':'The state is invalid.'
        }
        return json_response(response)
    # Check latitude and longitude
    if not (-90.0 <= float(params['latitude']) <= 90.0 and 
            -180.0 <= float(params['longitude']) <= 180.0):
        response = {
            'status':'FAIL',
            'error':'INVALID_COORDINATES',
            'message':'Latitude/longitude combination is invalid.'
        }
        return json_response(response)
    # Create the city
    city = City(name = params['name'], 
                state = params['state'],
                latitude = float(params['latitude']), 
                longitude = float(params['longitude']))
    city.save()
    response = {
        'status':'OK',
        'city':serialize_one(city)
    }
    return json_response(response)

@admin_required()
@validate('POST', ['id'])
def edit(request, params, admin):
    # Check if city exists
    if not City.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city doesn\'t exist.'
        }
        return json_response(response)
    city = City.objects.get(id = params['id'])
    # Go through all the params and change it accordingly
    if params['name'] is not None:
        if not (0 < len(params['name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'City name cannot be blank or over 50 characters.'
            }
            return json_response(response)
        else:
            city.name = params['name']
    if params['state'] is not None:
        params['state'] = params['state'].upper()
        if not params['state'] in BBOY_STATES:
            response = {
                'status':'FAIL',
                'error':'INVALID_STATE',
                'message':'The state is invalid.'
            }
            return json_response(response)
        else:
            city.state = params['state']
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
            city.latitude = float(params['latitude'])
            city.longitude = float(params['longitude'])
    # Save the changes
    city.save()
    response = {
        'status':'OK',
        'city':serialize_one(city)
    }
    return json_response(response)

@admin_required()
@validate('POST', ['id'])
def delete(request, params, admin):
    # Check if city exists
    if not City.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city doesn\'t exist.'
        }
        return json_response(response)
    city = City.objects.get(id = params['id'])
    # Check if there are profiles in the pseudo community or
    # if there are communities in the city (excluding the pseudo) 
    if (Profile.objects.filter(community = city.pseudo).exists() or 
       Community.objects.filter(~Q(id = city.pseudo.id), city = city).exists()):
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_EMPTY',
            'message':'Cannot delete a non-empty city.'
        }
        return json_response(response)
    # Delete the city and its pseudo community
    city.pseudo.delete()
    city.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)