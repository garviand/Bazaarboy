"""
Controller for community
"""

from django.db import transaction
from django.db.models import F
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
def index(request, id):
    pass

@admin_required()
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

@admin_required()
@validate('POST')
def edit(request, params):
    pass

@admin_required()
@validate('POST')
def delete(request, params):
    pass

@login_required()
@validate('POST', ['id'])
def follow(request, params):
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
    # Follow the community
    community = Community.objects.get(id = params['id'])
    user = User.objects.get(id = request.session['user'])
    rank = User_following.objects.filter(user = user).count()
    following = User_following(user = user, community = community, rank = rank)
    following.save()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id', 'rank'])
def rank_follow(request, params):
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
    user = User.objects.get(id = request.session['user'])
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
def unfollow(request, params):
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
    user = User.objects.get(id = request.session['user'])
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