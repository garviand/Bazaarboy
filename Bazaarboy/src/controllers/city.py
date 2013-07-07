"""
Controller for city
"""

from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
def index(request, id):
    pass

@admin_required()
@validate('GET', ['id'])
def city(request, params):
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
def create(request, params):
    """
    Create a new city
    """
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
def edit(request, params):
    pass

@admin_required()
@validate('POST', ['id'])
def delete(request, params):
    pass