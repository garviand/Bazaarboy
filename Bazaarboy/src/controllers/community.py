"""
Controller for community. Dev use only.
"""

from kernel.models import *
from src.serializer import serialize_one
from request import json_response, validate

@validate('GET', ['id'])
def city(request, params):
    city = City.objects.get(id = params['id'])
    return json_response(serialize_one(city))

@validate('GET', ['name', 'state', 'latitude', 'longitude'])
def create_city(request, params):
    city = City(name = params['name'], 
                state = params['state'],
                latitude = float(params['latitude']), 
                longitude = float(params['longitude']))
    city.save()
    return json_response(serialize_one(city))

@validate('GET', ['id'])
def community(request, params):
    community = Community.objects.get(id = params['id'])
    return json_response(serialize_one(community))

@validate('GET', ['name', 'description', 'city', 'latitude', 'longitude'])
def create_community(request, params):
    city = City.objects.get(id = params['city'])
    community = Community(name = params['name'], 
                          description = params['description'], 
                          city = params['city'], 
                          latitude = params['latitude'], 
                          longitude = params['longitude'])
    community.save()
    return json_response(serialize_one(community))