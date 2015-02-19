"""
Controller for rewards
"""

import cgi
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one
from src.email import sendReward
from datetime import timedelta
from django.utils import timezone
from src.regex import REGEX_EMAIL, REGEX_NAME, REGEX_SLUG
from django.shortcuts import render, redirect
from django.db.models import F, Q, Count

@login_required()
def index(request, user):
    """
    Rewards Dashboard
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    rewards = Reward.objects.filter(creator = profile, is_deleted = False)
    for reward in rewards:
        items = Reward_item.objects.filter(reward = reward)
        reward.given = items
    reward_items = Reward_item.objects.filter(owner = profile).order_by('-expiration_time')
    for item in reward_items:
        claims = Claim.objects.filter(item = item)
        item.claims = claims
        item.redeemed = claims.filter(is_redeemed = True).count()
    return render(request, 'reward/index.html', locals())

@login_required()
def new(request, user):
    """
    Rewards Create Page
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    return render(request, 'reward/new.html', locals())

@login_required()
@validate('POST', ['profile', 'name', 'description', 'value'], ['attachment'])
def create(request, params, user):
    """
    Create a reward
    """
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the profile.'
        }
        return json_response(response)
    params['name'] = cgi.escape(params['name'])
    if len(params['name']) > 150:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'The name must be within 150 characters.'
        }
        return json_response(response)
    params['description'] = cgi.escape(params['description'])
    if len(params['description']) > 350:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'The description must be within 350 characters.'
        }
        return json_response(response)
    if params['value'] <= 0:
        response = {
            'status':'FAIL',
            'error':'BAD_VALUE',
            'message':'Reward value must be a positive number.'
        }
        return json_response(response)
    reward = Reward (creator = profile, name = params['name'], description = params['description'], value = params['value'])
    if params['attachment'] is not None:
        if Pdf.objects.filter(id = params['attachment']).exists():
            reward.attachment = Pdf.objects.get(id = params['attachment'])
        else:
            response = {
                'status':'FAIL',
                'error':'INVALID_ATTACHMENT',
                'message':'The attachment does not exist.'
            }
            return json_response(response)
    reward.save()
    response = {
        'status':'OK',
        'reward':serialize_one(reward)
    }
    return json_response(response)

@login_required()
@validate('POST', ['reward', 'name', 'description', 'value'], ['attachment'])
def edit(request, params, user):
    """
    Edit a reward
    """
    if not Reward.objects.filter(id = params['reward']).exists():
        response = {
            'status':'FAIL',
            'error':'REWARD_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    reward = Reward.objects.get(id = params['reward'])
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = reward.creator, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the reward.'
        }
        return json_response(response)
    params['name'] = cgi.escape(params['name'])
    if len(params['name']) > 150:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'The name must be within 150 characters.'
        }
        return json_response(response)
    params['description'] = cgi.escape(params['description'])
    if len(params['description']) > 350:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'The description must be within 350 characters.'
        }
        return json_response(response)
    if params['value'] <= 0:
        response = {
            'status':'FAIL',
            'error':'BAD_VALUE',
            'message':'Reward value must be a positive number.'
        }
        return json_response(response)
    reward.name = params['name']
    reward.description = params['description']
    reward.value = params['value']
    if params['attachment'] is not None:
        if Pdf.objects.filter(id = params['attachment']).exists():
            reward.attachment = Pdf.objects.get(id = params['attachment'])
        else:
            response = {
                'status':'FAIL',
                'error':'INVALID_ATTACHMENT',
                'message':'The attachment does not exist.'
            }
            return json_response(response)
    else:
        reward.attachment = None
    reward.save()
    response = {
        'status':'OK',
        'reward':serialize_one(reward)
    }
    return json_response(response)

@login_required()
@validate('POST', ['reward', 'owner', 'quantity', 'expiration_time'])
def add_item(request, params, user):
    if not Reward.objects.filter(id = params['reward']).exists():
        response = {
            'status':'FAIL',
            'error':'REWARD_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    reward = Reward.objects.get(id = params['reward'])
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = reward.creator, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the reward.'
        }
        return json_response(response)
    if not Profile.objects.filter(id = params['owner']).exists():
        response = {
            'status':'FAIL',
            'error':'NO_PROFILE',
            'message':'The profile you are sending to does not exist.'
        }
        return json_response(response)
    params['quantity'] = int(params['quantity'])
    if params['quantity'] <= 0:
        response = {
            'status':'FAIL',
            'error':'NON_POSITIVE_QUANTITY',
            'message':'Quantity must be a positive integer.'
        }
        return json_response(response)
    owner = Profile.objects.get(id = params['owner'])
    if params['expiration_time'] < timezone.now():
        response = {
            'status':'FAIL',
            'error':'EXPIRE_BEFORE_NOW',
            'message':'The expiration date must be in the future.'
        }
        return json_response(response)
    reward_item = Reward_item(reward = reward, owner = owner, quantity = params['quantity'], expiration_time = params['expiration_time'])
    reward_item.save()
    response = {
        'status':'OK',
        'reward_item':serialize_one(reward_item)
    }
    return json_response(response)

@login_required()
@validate('POST', ['item'], ['owner', 'email'])
def add_claim(request, params, user):
    if not Reward_item.objects.filter(id = params['item']).exists():
        response = {
            'status':'FAIL',
            'error':'REWARD_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    item = Reward_item.objects.get(id = params['item'])
    if item.quantity == 0:
        response = {
            'status':'FAIL',
            'error':'ZERO_QUANTITY',
            'message':'You don\'t have any more of these items to give away.'
        }
        return json_response(response)
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = item.reward.creator, user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the reward.'
        }
        return json_response(response)
    if params['owner'] is None:
        if not params['email'] or not REGEX_EMAIL.match(params['email']):
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL',
                'message':'Email format is invalid.'
            }
            return json_response(response)
        email = params['email']
        owner = None
    else:
        if not User.objects.filter(id = params['owner']).exists():
            response = {
                'status':'FAIL',
                'error':'INVALID_USER',
                'message':'The user does not exist.'
            }
            return json_response(response)
        owner = User.objects.get(id = params['owner'])
        email = owner.email
    claim = Claim(email = email, owner = owner, item = item)
    item.quantity -= 1
    item.save()
    claim.save()
    sendReward(claim)
    response = {
        'status':'OK',
        'reward_item':serialize_one(item),
        'claim':serialize_one(claim)
    }
    return json_response(response)