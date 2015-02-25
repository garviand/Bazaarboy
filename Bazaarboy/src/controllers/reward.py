"""
Controller for rewards
"""

import cgi
import re
import stripe
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one
from src.email import sendReward
from src.config import *
from datetime import timedelta
from django.utils import timezone
from src.regex import REGEX_EMAIL, REGEX_NAME, REGEX_SLUG
from django.shortcuts import render, redirect
from django.db.models import F, Q, Count
from src.sms import sendClaimMMS

import pdb

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
    reward_items = Reward_item.objects.filter(owner = profile, expiration_time__gte = timezone.now()).order_by('expiration_time')
    for item in reward_items:
        claims = Claim.objects.filter(item = item)
        item.claims = claims
        item.redeemed = claims.filter(is_redeemed = True).count()
    publishable_key = STRIPE_PUBLISHABLE_KEY
    if Subscription.objects.filter(owner = profile).exists():
        subscription = Subscription.objects.get(owner = profile)
    else:
        subscription = None
    return render(request, 'reward/index.html', locals())

@login_required()
def new(request, user):
    """
    Rewards Create Page
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    return render(request, 'reward/new.html', locals())

@validate('GET', ['id', 'token'])
def claim(request, params):
    if not Claim.objects.filter(id = params['id'], token = params['token']).exists():
        claim = None
    else:
        claim = Claim.objects.get(id = params['id'])
    return render(request, 'reward/claim.html', locals())

@login_required()
def manage(request, reward, user):
    if not Reward.objects.filter(id = reward).exists():
        response = {
            'status':'FAIL',
            'error':'REWARD_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    reward = Reward.objects.get(id = reward)
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = reward.creator, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the reward.'
        }
        return json_response(response)
    claims = Claim.objects.filter(item__reward = reward, is_claimed = True).order_by("item__expiration_time")
    return render(request, 'reward/manage.html', locals())

@login_required()
@validate('POST', ['stripe_token', 'profile', 'email'])
def subscribe(request, params, user):
    """
    Subscribe to rewards account
    """
    if not Profile.objects.filter(id = params['profile']).exists():
        response = {
            'status':'FAIL',
            'error':'PROFILE_NOT_FOUND',
            'message':'The profile doesn\'t exist.'
        }
        return json_response(response)
    profile = Profile.objects.get(id = params['profile'])
    if not Profile_manager.objects.filter(profile = profile, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the profile.'
        }
        return json_response(response)
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    stripe.api_key = STRIPE_SECRET_KEY
    try:
        customer = stripe.Customer.create(
            description = "Gifts Account for " + params['email'],
            source = params['stripe_token'],
            email = params['email'],
            plan = "gifts"
        )
        subscription = Subscription(owner = profile, customer_id = customer.id, subscription_id = customer.subscriptions.data[0].id, plan_id = 'gifts', credits = 0)
        subscription.save()
    except stripe.CardError, e:
        response = {
            'status':'FAIL',
            'error':'CARD_DECLINED',
            'message':'The card is declined.'
        }
        return json_response(response)
    response = {
        'status':'OK',
        'subscription': serialize_one(subscription)
    }
    return json_response(response)

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

@login_required()
@validate('POST', ['claim_id', 'claim_token', 'first_name', 'last_name'], ['phone'])
def complete_claim(request, params, user):
    if not Claim.objects.filter(id = params['claim_id'], token = params['claim_token']).exists():
        response = {
            'status':'FAIL',
            'error':'CLAIM_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    claim = Claim.objects.get(id = params['claim_id'])
    if claim.is_claimed:
        response = {
            'status':'FAIL',
            'error':'ALREADY_CLAIMED',
            'message':'This reward has already been claimed.'
        }
        return json_response(response)
    sendMMS = False
    if params['phone'] is not None:
        params['phone'] = re.compile(r'[^\d]+').sub('', params['phone'])
        if len(params['phone']) != 10:
            response = {
                'status':'FAIL',
                'error':'INVALID_PHONE',
                'message':'The phone number is invalid. Just use numbers (no spaces or \'-\').'
            }
            return json_response(response)
        sendMMS = True
    if User.objects.filter(email = claim.email).exists():
        claim.owner = User.objects.get(email = claim.email)
        claim.owner.first_name = params['first_name']
        claim.owner.last_name = params['last_name']
    elif claim.owner:
        claim.owner.email = claim.email
        claim.owner.first_name = params['first_name']
        claim.owner.last_name = params['last_name']
    else:
        claim.owner = User(email = claim.email, first_name = params['first_name'], last_name = params['last_name'])
    if Subscription.objects.filter(owner = claim.item.reward.creator, plan_id = 'gifts'):
        subscription = Subscription.objects.get(owner = claim.item.reward.creator, plan_id = 'gifts')
        if subscription.credits > 0:
            subscription.credits -= 1
            subscription.save()
        else:
            stripe.api_key = STRIPE_SECRET_KEY
            try:
                invoice = stripe.InvoiceItem.create(
                    customer = subscription.customer_id,
                    subscription = subscription.subscription_id,
                    amount = 100,
                    currency = "usd",
                    description = claim.item.reward.name  + " claimed by " + claim.owner.email
                )
            except stripe.error.StripeError, e:
                response = {
                    'status':'FAIL',
                    'error':'STRIPE_ERROR',
                    'message':'The reward is not available.'
                }
                return json_response(response)
    claim.owner.save()
    claim.is_claimed = True
    claim.claimed_time = timezone.now()
    claim.save()
    if sendMMS:
        claim.owner.phone = params['phone']
        claim.owner.save()
        sendClaimMMS(claim)
    response = {
        'status':'OK',
        'claim':serialize_one(claim)
    }
    return json_response(response)

@login_required()
@validate('POST', ['claim_id'])
def redeem(request, params, user):
    if not Claim.objects.filter(id = params['claim_id']).exists():
        response = {
            'status':'FAIL',
            'error':'CLAIM_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    claim = Claim.objects.get(id = params['claim_id'])
    if claim.is_redeemed:
        response = {
            'status':'FAIL',
            'error':'ALREADY_REDEEMED',
            'message':'This reward has already been redeemed.'
        }
        return json_response(response)
    if not Profile_manager.objects.filter(profile = claim.item.reward.creator, 
                                          user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the reward.'
        }
        return json_response(response)
    claim.is_redeemed = True
    claim.redemption_time = timezone.now()
    claim.save()
    response = {
        'status':'OK',
        'claim':serialize_one(claim)
    }
    return json_response(response)