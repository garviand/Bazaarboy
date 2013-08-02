"""
Controller for community
"""

from django.db import transaction
from django.db.models import F
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
def index(request, id, user):
    pass

@admin_required()
@validate('GET', ['id'])
def community(request, params, admin):
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
def create(request, params, admin):
    """
    Create a new community
    """
    # Check the city
    if not City.objects.filter(id = params['city']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city doesn\'t exist.'
        }
        return json_response(response)
    city = City.objects.get(id = params['city'])
    # Check if the name is too long
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'The name cannot be over 50 characters.'
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
    # Create the community
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

@admin_required()
@validate('POST', ['id'], ['name', 'description', 'latitude', 'longitude'])
def edit(request, params, admin):
    """
    Edit an existing community
    """
    # Check if community exists
    if not Community.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist.'
        }
        return json_response(response)
    community = Community.objects.get(id = params['id'])
    # Go through all the params and change it accordingly
    if params['name'] is not None:
        if not (0 < len(params['name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Community name cannot be blank or over 50 characters.'
            }
            return json_response(response)
        else:
            community.name = params['name']
    if params['description'] is not None:
        community.description = params['description']
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
            community.latitude = float(params['latitude'])
            community.longitude = float(params['longitude'])
    # Save the changes
    community.save()
    response = {
        'status':'OK',
        'community':serialize_one(community)
    }
    return json_response(response)

@admin_required()
@validate('POST', ['id'])
def delete(request, params, admin):
    """
    Delete a community
    """
    # Check if community exists
    if not Community.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist.'
        }
        return json_response(response)
    community = Community.objects.get(id = params['id'])
    # Check if the community is a city's pseudo community
    if community.city.pseudo.id == community.id
        response = {
            'status':'FAIL',
            'error':'PSEUDO_COMMUNITY',
            'message':'You cannot delete a pseudo community of a city.'
        }
        return json_response(response)
    # Check if there are profiles under the community
    if Profile.objects.filter(community = community).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_EMPTY',
            'message':'Cannot delete a non-empty community.'
        }
        return json_response(response)
    # Delete the community
    community.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def follow(request, params, user):
    """
    Follow a community
    """
    # Check if community exists
    if not Community.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist.'
        }
        return json_response(response)
    community = Community.objects.get(id = params['id'])
    # Follow the community
    rank = User_following.objects.filter(user = user).count()
    following = User_following(user = user, community = community, rank = rank)
    following.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'rank'])
def rank_follow(request, params, user):
    """
    Set the rank of a community following
    """
    # Check if community exists
    if not Community.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist.'
        }
        return json_response(response)
    community = Community.objects.get(id = params['id'])
    # Check if the user is following the community
    if not User_following.objects.filter(user = user, community = community) \
                                 .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_FOLLOWING',
            'message':'You are not following this community.'
        }
        return json_response(response)
    # Check if the rank is out of bounds
    params['rank'] = int(params['rank'])
    followings = User_following.objects.filter(user = user)
    if not (0 <= params['rank'] < followings.count()):
        response = {
            'status':'FAIL',
            'error':'RANK_OUT_OF_BOUNDS'
        }
        return json_response(response)
    # Rerank the followings
    with transaction.commit_on_success():
        followings = sorted(followings, key = lambda f: f.rank)
        for i in range(params['rank'], followings.count()):
            following = followings[i]
            if following.community == community:
                following.rank = params['rank']
                following.save()
                break
            else:
                following.rank = F('rank') + 1
                following.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def unfollow(request, params, user):
    """
    Unfollow a community
    """
    # Check if community exists
    if not Community.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'COMMUNITY_NOT_FOUND',
            'message':'The community doesn\'t exist.'
        }
        return json_response(response)
    community = Community.objects.get(id = params['id'])
    # Check if the user is following the community
    if not User_following.objects.filter(user = user, community = community) \
                                 .exists():
        response = {
            'status':'FAIL',
            'error':'NOT_FOLLOWING',
            'message':'You are not following this community.'
        }
        return json_response(response)
    # Rerank the followings
    with transaction.commit_on_success():
        unfollowing = User_following.objects.filter(user = user, 
                                                    community = community)
        followings = sorted(followings, key = lambda f: f.rank)
        for i in range(unfollowing.rank + 1, followings.count()):
            following = followings[i]
            following.rank = F('rank') - 1
            following.save()
        unfollowing.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)