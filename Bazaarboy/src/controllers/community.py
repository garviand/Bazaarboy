"""
Controller for community
"""

from kernel.models import *
from src.controllers.request import json_response, validate, admin_required
from src.serializer import serialize_one

@validate('GET', ['id'])
def community(request, params):
    """
    Returns the serialized data about a community
    """
    if not Community.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist.'
        }
        return json_response(response)
    community = Community.objects.get(id = params['id'])
    response = {
        'status':'OK',
        'community':serialize_one(community)
    }
    return json_response(response)

@admin_required()
@validate('POST', ['name', 'description', 'city', 'latitude', 'longitude'])
def create(request, params):
    """
    Create a new community
    """
    if not City.objects.filter(id = params['city']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city doesn\'t exist.'
        }
    city = City.objects.get(id = params['city'])
    community = Community(name = params['name'], 
                          description = params['description'], 
                          city = city, 
                          latitude = params['latitude'], 
                          longitude = params['longitude'])
    community.save()
    response = {
        'status':'OK',
        'community':serialize_one(community)
    }
    return json_response(response)