"""
Controller for rewards
"""

import cgi
import re
import stripe
import ordereddict
from giphypop import Giphy
import json
import simplejson
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one
from src.email import sendReward, sendRewardSend
from src.config import *
from datetime import timedelta
from django.utils import timezone
from src.regex import REGEX_EMAIL, REGEX_NAME, REGEX_SLUG
from django.shortcuts import render, redirect
from django.db.models import F, Q, Count
from src.sms import sendClaimMMS
from urlparse import urlparse
import urllib2
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

import pdb

@login_required()
def index(request, user):
    """
    Rewards Dashboard
    """
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    rewards = Reward.objects.filter(creator = profile).order_by('is_deleted')
    deletedRewards = Reward.objects.filter(creator = profile).count()
    for reward in rewards:
        items = Reward_item.objects.filter(reward = reward)
        reward.given = items
        reward.transferred = Reward_item.objects.filter(reward = reward).aggregate(Sum('received'))['received__sum']
        if reward.transferred is None:
            reward.transferred = 0
        reward.sent = Claim.objects.filter(item__reward = reward).count()
        if Reward_giveaway.objects.filter(item__reward = reward).aggregate(Sum('quantity'))['quantity__sum'] is not None:
            reward.sent += Reward_giveaway.objects.filter(item__reward = reward).aggregate(Sum('quantity'))['quantity__sum']
        reward.claimed = Claim.objects.filter(item__reward = reward, is_claimed = True).count()
        reward.redeemed = Claim.objects.filter(item__reward = reward, is_redeemed = True).count()
    reward_items = Reward_item.objects.filter(owner = profile, expiration_time__gte = timezone.now(), quantity__gt = 0, is_deleted = False).order_by('expiration_time')
    for item in reward_items:
        claims = Claim.objects.filter(item = item)
        item.claims = claims
        item.redeemed = claims.filter(is_redeemed = True).count()
    giveaways = Reward_giveaway.objects.filter(item__owner = profile, item__expiration_time__gte = timezone.now(), quantity__gt = 0, item__is_deleted = False).order_by('item__expiration_time')
    publishable_key = STRIPE_PUBLISHABLE_KEY
    totalRewards = Reward_item.objects.filter(reward__creator = profile).aggregate(Sum('received'))['received__sum']
    if totalRewards is None:
        totalRewards = 0
    totalSends = Reward_send.objects.filter(reward__creator = profile, claimed = False).aggregate(Sum('quantity'))['quantity__sum']
    if totalSends is None:
        totalSends = 0
    totalSent = totalRewards + totalSends
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
        extra_fields = []
        if claim.item.reward.extra_fields:
            custom_fields = simplejson.loads(claim.item.reward.extra_fields, object_pairs_hook=ordereddict.OrderedDict)
            for field in ordereddict.OrderedDict(sorted(custom_fields.items())).items():
                extra_fields.append(field[1])
        reward_item = claim.item
    return render(request, 'reward/claim.html', locals())

@validate('GET')
def giveaway(request, params, token):
    if not Reward_giveaway.objects.filter(token = token).exists():
        giveaway = None
    else:
        giveaway = Reward_giveaway.objects.get(token = token)
        extra_fields = []
        if giveaway.item.reward.extra_fields:
            custom_fields = simplejson.loads(giveaway.item.reward.extra_fields, object_pairs_hook=ordereddict.OrderedDict)
            for field in ordereddict.OrderedDict(sorted(custom_fields.items())).items():
                extra_fields.append(field[1])
        reward_item = giveaway.item
    return render(request, 'reward/claim.html', locals())

@validate('GET', ['id', 'code'])
def redeem_confirm(request, params):
    now = timezone.now()
    if not Claim.objects.filter(id = params['id'], code = params['code']).exists():
        claim = None
    else:
        claim = Claim.objects.get(id = params['id'])
        extra_fields = []
        if claim.item.reward.extra_fields:
            custom_fields = simplejson.loads(claim.item.reward.extra_fields, object_pairs_hook=ordereddict.OrderedDict)
            for field in ordereddict.OrderedDict(sorted(custom_fields.items())).items():
                extra_fields.append(field[1])
    return render(request, 'reward/redeem.html', locals())

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
    for claim in claims:
        try:
            fields = json.loads(claim.extra_fields)
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            claim.extra_fields = fields
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
        totalRewards = Reward_item.objects.filter(reward__creator = profile).aggregate(Sum('received'))['received__sum']
        if totalRewards is None:
            totalRewards = 0
        totalSends = Reward_send.objects.filter(reward__creator = profile, claimed = False).aggregate(Sum('quantity'))['quantity__sum']
        if totalSends is None:
            totalSends = 0
        previouslyClaimed = len(Claim.objects.filter(item__reward__creator = profile, is_claimed = True))
        totalCredits = totalRewards + totalSends - previouslyClaimed
        subscription = Subscription(owner = profile, customer_id = customer.id, subscription_id = customer.subscriptions.data[0].id, plan_id = 'gifts', credits = totalCredits)
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
@validate('POST', ['profile', 'name', 'description', 'value', 'gif'], ['attachment', 'extra_fields'])
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
    reward.save()
    if params['extra_fields'] is not None:
        try:
            fields = json.loads(params['extra_fields'])
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            reward.extra_fields = json.dumps(fields)
    if params['attachment'] is not None:
        if params['gif'] == 'true':
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(params['attachment']).read())
            img_temp.flush()
            img_filename = urlparse(params['attachment']).path.split('/')[-1]
            pdf = Pdf(source = File(img_temp), name = img_filename)
            pdf.source.save(uuid.uuid4().hex+img_filename, File(img_temp))
            pdf.save()
            reward.attachment = pdf
        else:
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
@validate('POST', ['reward'])
def delete(request, params, user):
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
    reward.is_deleted = True
    reward.save()
    response = {
        'status':'OK',
        'reward':serialize_one(reward)
    }
    return json_response(response)

@login_required()
@validate('POST', ['reward', 'quantity', 'expiration_time'], ['owner', 'email'])
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
    params['quantity'] = int(params['quantity'])
    if params['quantity'] <= 0:
        response = {
            'status':'FAIL',
            'error':'NON_POSITIVE_QUANTITY',
            'message':'Quantity must be a positive integer.'
        }
        return json_response(response)
    if params['owner'] is not None:
        if not Profile.objects.filter(id = params['owner']).exists():
            response = {
                'status':'FAIL',
                'error':'NO_PROFILE',
                'message':'The profile you are sending to does not exist.'
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
        reward_item = Reward_item(reward = reward, owner = owner, quantity = params['quantity'], received = params['quantity'], expiration_time = params['expiration_time'])
        reward_item.save()
        response = {
            'status':'OK',
            'reward_item':serialize_one(reward_item)
        }
        return json_response(response)
    elif params['email'] is not None:
        if not REGEX_EMAIL.match(params['email']):
            response = {
                'status':'FAIL',
                'error':'INVALID_EMAIL',
                'message':'The email you entered is invalid.'
            }
            return json_response(response)
        reward_send = Reward_send(reward = reward, email = params['email'], quantity = params['quantity'], expiration_time = params['expiration_time'])
        reward_send.save()
        sendRewardSend(reward_send)
        response = {
            'status':'OK',
            'reward_send':serialize_one(reward_send)
        }
        return json_response(response)
    else:
        response = {
            'status':'FAIL',
            'error':'EMAIL_OR_OWNER',
            'message':'Must choose an email or profile.'
        }
        return json_response(response)

@login_required()
@validate('POST', ['item'])
def delete_item(request, params, user):
    if not Reward_item.objects.filter(id = params['item']).exists():
        response = {
            'status':'FAIL',
            'error':'REWARD_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    item = Reward_item.objects.get(id = params['item'])
    # Check if the user is a manager of the profile
    if not Profile_manager.objects.filter(profile = item.owner, user = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the reward.'
        }
        return json_response(response)
    item.is_deleted = True
    item.save()
    response = {
        'status':'OK',
        'reward_item':serialize_one(item)
    }
    return json_response(response)


@login_required()
@validate('POST', ['item'], ['owner', 'email', 'message'])
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
    if not Profile_manager.objects.filter(profile = item.owner, user = user).exists():
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
    if params['message']:
        claimMessage = params['message']
    else:
        claimMessage = ''
    claim = Claim(email = email, owner = owner, item = item, message = claimMessage)
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


@validate('POST', ['claim_id', 'claim_token', 'first_name', 'last_name'], ['phone', 'extra_fields'])
def complete_claim(request, params):
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
    else:
        response = {
            'status':'FAIL',
            'error':'INVALID_PHONE',
            'message':'The phone number is invalid. Just use numbers (no spaces or \'-\').'
        }
        return json_response(response)
    if User.objects.filter(email = claim.email).exists():
        claim.owner = User.objects.get(email = claim.email)
        claim.owner.first_name = params['first_name']
        claim.owner.last_name = params['last_name']
    elif claim.owner is not None:
        claim.owner.email = claim.email
        claim.owner.first_name = params['first_name']
        claim.owner.last_name = params['last_name']
    else:
        newUser = User(email = claim.email, first_name = params['first_name'], last_name = params['last_name'])
        newUser.save()
        claim.save()
        claim.owner = newUser
    claim.save()
    claim.is_claimed = True
    claim.claimed_time = timezone.now()
    if params['extra_fields'] is not None:
        try:
            fields = json.loads(params['extra_fields'])
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            claim.extra_fields = json.dumps(fields)
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

@login_check()
@validate('POST', ['claim_id'], ['token'])
def redeem(request, params, user):
    if not Claim.objects.filter(id = params['claim_id']).exists():
        response = {
            'status':'FAIL',
            'error':'CLAIM_NOT_FOUND',
            'message':'The gift doesn\'t exist.'
        }
        return json_response(response)
    claim = Claim.objects.get(id = params['claim_id'])
    if claim.is_redeemed:
        response = {
            'status':'FAIL',
            'error':'ALREADY_REDEEMED',
            'message':'This gift has already been redeemed.'
        }
        return json_response(response)
    token_pass = False
    if params['token'] is not None:
        if claim.token == params['token']:
            token_pass = True
    if not Profile_manager.objects.filter(profile = claim.item.reward.creator, user = user).exists() and token_pass is False:
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

@login_required()
@validate('POST', ['reward', 'quantity', 'expiration_time'])
def create_giveaway(request, params, user):
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
    params['quantity'] = int(params['quantity'])
    if params['quantity'] <= 0:
        response = {
            'status':'FAIL',
            'error':'NON_POSITIVE_QUANTITY',
            'message':'Quantity must be a positive integer.'
        }
        return json_response(response)
    if params['expiration_time'] < timezone.now():
        response = {
            'status':'FAIL',
            'error':'EXPIRE_BEFORE_NOW',
            'message':'The expiration date must be in the future.'
        }
        return json_response(response)
    reward_item = Reward_item(reward = reward, owner = reward.creator, quantity = 0, received = params['quantity'], expiration_time = params['expiration_time'])
    reward_item.save()
    giveaway = Reward_giveaway(item = reward_item, quantity = params['quantity'])
    giveaway.save()
    response = {
        'status':'OK',
        'giveaway': serialize_one(giveaway),
        'reward_item':serialize_one(reward_item)
    }
    return json_response(response)

@validate('POST', ['giveaway_id', 'giveaway_token', 'first_name', 'last_name', 'email'], ['phone', 'extra_fields'])
def complete_giveaway(request, params):
    if not Reward_giveaway.objects.filter(id = params['giveaway_id'], token = params['giveaway_token']).exists():
        response = {
            'status':'FAIL',
            'error':'CLAIM_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    giveaway = Reward_giveaway.objects.get(id = params['giveaway_id'])
    if giveaway.quantity == 0:
        response = {
            'status':'FAIL',
            'error':'ALL_CLAIMED',
            'message':'Sorry, you are too late. All of the gifts have already been claimed!'
        }
        return json_response(response)
    if giveaway.item.expiration_time < timezone.now():
        response = {
            'status':'FAIL',
            'error':'EXPIRE_BEFORE_NOW',
            'message':'The gift has expired.'
        }
        return json_response(response)
    sendMMS = False
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'You must enter a valid email address.'
        }
        return json_response(response)
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
    else:
        response = {
            'status':'FAIL',
            'error':'INVALID_PHONE',
            'message':'The phone number is invalid. Just use numbers (no spaces or \'-\').'
        }
        return json_response(response)
    if Claim.objects.filter(owner__phone = params['phone'], item = giveaway.item).exists():
        response = {
            'status':'FAIL',
            'error':'ALREADY_CLAIMED',
            'message':'This phone # has already claimed this gift. Only one gift allowed per person.'
        }
        return json_response(response)
    claim = Claim(email = params['email'], item = giveaway.item)
    claim.save()
    giveaway.quantity -= 1
    giveaway.save()
    if User.objects.filter(email = claim.email).exists():
        claim.owner = User.objects.get(email = claim.email)
        claim.owner.first_name = params['first_name']
        claim.owner.last_name = params['last_name']
    elif claim.owner is not None:
        claim.owner.email = claim.email
        claim.owner.first_name = params['first_name']
        claim.owner.last_name = params['last_name']
    else:
        newUser = User(email = claim.email, first_name = params['first_name'], last_name = params['last_name'])
        newUser.save()
        claim.save()
        claim.owner = newUser
    claim.save()
    claim.is_claimed = True
    claim.claimed_time = timezone.now()
    if params['extra_fields'] is not None:
        try:
            fields = json.loads(params['extra_fields'])
        except:
            response = {
                'status':'FAIL',
                'error':'INVALID_FIELD_FORMAT',
                'message':'The extra field format is not correct.'
            }
            return json_response(response)
        finally:
            claim.extra_fields = json.dumps(fields)
    claim.save()
    if sendMMS:
        claim.owner.phone = params['phone']
        claim.owner.save()
        sendClaimMMS(claim)
    response = {
        'status':'OK',
        'claim':serialize_one(claim),
        'giveaway':serialize_one(giveaway)
    }
    return json_response(response)

def send_inventory(reward, recipients, expiration):
    """
    Send rewards directly from inventory
    """
    reward_item = Reward_item(reward = reward, owner = reward.creator, quantity = 0, received = len(recipients), expiration_time = expiration)
    reward_item.save()
    sent = 0
    for recipient in recipients:
        if REGEX_EMAIL.match(recipient):
            claim = Claim(email = recipient, item = reward_item)
            claim.save()
            sent += 1
    response = {
        'status':'OK',
        'reward_item': serialize_one(reward_item),
        'sent': str(sent)
    }
    return json_response(response)


@login_required()
@validate('GET', ['q'])
def search_gifs(request, params, user):
    g = Giphy()
    results = [x for x in g.search(term=params['q'], limit=12)]
    response = {
        'status':'OK',
        'gifs': json.dumps(results)
    }
    return json_response(response)