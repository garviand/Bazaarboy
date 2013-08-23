"""
Controller for fundraisers
"""

import os
from datetime import timedelta
from django.db.models import F
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from celery import task
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.controllers.wepay import create_checkout
from src.sanitizer import sanitize_redactor_input
from src.serializer import serialize_one

FORMAT_DATETIME = '%Y-%m-%d %X'

@login_check()
@validate('GET', [], ['token'])
def index(request, id, params, user):
    """
    Fundraiser event page
    """
    """
    if not Fundraiser.objects.filter(id = id).exists():
        raise Http404
    fundraiser = Fundraiser.objects.select_related().get(id = id)
    editable = False
    if fundraiser.owner is not None:
        editable = (user is not None and 
                    Profile_manager.objects.filter(user = user, 
                                                   profile = fundraiser.owner) \
                                           .exists())
        if not editable and not fundraiser.is_launched:
            return redirect('index')
    elif (params['token'] is not None and 
          fundraiser.access_token == params['token']):
        editable = True
    else:
        return redirect('index')
    """
    return render(request, 'fundraiser/index.html', locals())

@login_required()
@validate('GET', ['id'])
def fundraiser(request, params, user):
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
          ['profile', 'name', 'description', 'category', 'goal', 'deadline'], 
          ['summary', 'tags', 'location', 'latitude', 'longitude', 
           'is_private', 'token'])
def create(request, params, user):
    """
    Create a new fundraiser
    """
    # Check if the name is too long
    params['name'] = params['name'].strip()
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'The name is too long, maximum 50 charaters.'
        }
        return json_response(response)
    # Check the goal
    params['goal'] = float(params['goal'])
    if params['goal'] <= 0:
        response = {
            'status':'FAIL',
            'error':'INVALID_GOAL',
            'message':'The goal is invalid.'
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
                            category = params['category'], 
                            owner = profile, 
                            goal = params['goal'], 
                            deadline = params['deadline'])
    # Check if summary and tags are legal
    if params['summary'] is not None:
        if len(params['summary']) > 100:
            response = {
                'status':'FAIL',
                'error':'SUMMARY_TOO_LONG',
                'message':'The summary must be within 150 characters.'
            }
            return json_response(response)
        else:
            fundraiser.summary = params['summary']
    if params['tags'] is not None:
        if len(params['tags']) > 50:
            response = {
                'status':'FAIL',
                'error':'TAGS_TOO_LONG',
                'message':'The tags must be within 150 characters.'
            }
            return json_response(response)
        else:
            fundraiser.tags = params['tags']
    # Check if the location is specified
    if params['location'] is not None:
        if len(params['location']) > 100:
            response = {
                'status':'FAIL',
                'error':'LOCATION_TOO_LONG',
                'message':'The location must be within 100 characters.'
            }
            return json_response(response)
        else:
            fundraiser.location = params['location']
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
    # Check if the user has logged in
    if user is not None:
        # If so, check if the profile is valid
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
        # Set the owner of the fundraiser to the specified profile
        fundraiser.owner = profile
    else:
        # Otherwise, generate an access token for the anonymous user
        fundraiser.access_token = os.urandom(128).encode('base_64')[:128]
    # Save to database
    fundraiser.save()
    response = {
        'status':'OK',
        'fundraiser':serialize_one(fundraiser)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'cover', 'caption', 'summary', 'tags', 
           'goal', 'deadline', 'location', 'latitude', 'longitude', 
           'category', 'is_private', 'token'])
def edit(request, params, user):
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
    # Check if user has logged in
    if user is not None:
        # If so, check if user has permission for the fundraiser
        if not Profile_manager.objects.filter(user = user, 
                                              profile = fundraiser.owner) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if (params['token'] is None or 
            fundraiser.access_token != params['token']):
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    # Go through all params and edit the fundraiser accordingly
    if params['goal'] is not None:
        if fundraiser.is_launched:
            response = {
                'status':'FAIL',
                'error':'LAUNCHED_FUNDRAISER',
                'message':'You can\'t change the goal while launched.'
            }
            return json_response(response)
        params['goal'] = float(params['goal'])
        if params['goal'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_GOAL',
                'message':'The goal is too small.'
            }
        else:
            fundraiser.goal = params['goal']
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
        params['name'] = params['name'].strip()
        if not (0 < len(params['name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Name cannot be blank or more than 50 charaters.'
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
    if params['cover'] is not None:
        if params['cover'].lower() == 'delete':
            if fundraiser.cover is not None:
                oldCover = Image.objects.get(id = fundraiser.cover.id)
                oldCover.delete()
                fundraiser.cover = None
        elif not Image.objects.filter(id = params['cover']).exists():
            response = {
                'status':'FAIL',
                'error':'COVER_IMAGE_NOT_FOUND',
                'message':'The cover image doesn\'t exist.'
            }
            return json_response(response)
        else:
            cover = Image.objects.get(id = params['cover'])
            if fundraiser.cover is not None:
                oldCover = Image.objects.get(id = fundraiser.cover.id)
                oldCover.delete()
            cover.is_archived = True
            cover.save()
            fundraiser.cover = cover
    if params['caption'] is not None:
        if fundraiser.cover is None:
            response = {
                'status':'FAIL',
                'error':'NO_COVER',
                'message':'You must set a cover image before adding caption.'
            }
            return json_response(response)
        elif len(params['caption']) > 100:
            response = {
                'status':'FAIL',
                'error':'CAPTION_TOO_LONG',
                'message':'The caption must be within 100 characters.'
            }
            return json_response(response)
        else:
            fundraiser.cover.caption = params['caption']
            fundraiser.cover.save()
    if params['summary'] is not None:
        if len(params['summary']) > 100:
            response = {
                'status':'FAIL',
                'error':'SUMMARY_TOO_LONG',
                'message':'The summary must be within 150 characters.'
            }
            return json_response(response)
        else:
            fundraiser.summary = params['summary']
    if params['tags'] is not None:
        if len(params['tags']) > 50:
            response = {
                'status':'FAIL',
                'error':'TAGS_TOO_LONG',
                'message':'The tags must be within 150 characters.'
            }
            return json_response(response)
        else:
            fundraiser.tags = params['tags']
    if params['location'] is not None:
        if len(params['location']) > 100:
            response = {
                'status':'FAIL',
                'error':'LOCATION_TOO_LONG',
                'message':'The location must be within 100 characters.'
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
def launch(request, params, user):
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
def delaunch(request, params, user):
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
    # Check if the deadline has passed
    if fundraiser.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'DEADLINE_PAST_DUE',
            'message':'The deadline has passed.'
        }
        return json_response(response)
    # Refund all the donations
    rewards = Reward.objects.filter(fundraiser = fundraiser)
    for reward in rewards:
        donations = Donation.objects.filter(reward = reward)
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
@validate('POST', ['id'], ['token'])
def delete(request, params, user):
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
    # Check if user has logged in
    if user is not None:
        # If so, check if user has permission for the fundraiser
        if not Profile_manager.objects.filter(user = user, 
                                              profile = fundraiser.owner) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if (params['token'] is None or 
            fundraiser.access_token != params['token']):
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
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
@validate('POST', ['fundraiser', 'name', 'description', 'price'], 
          ['quantity', 'token'])
def create_reward(request, params, user):
    """
    Create a reward for the fundraiser
    """
    # Check if fundraiser is valid
    if not fundraiser.objects.filter(id = params['fundraiser']):
        response = {
            'status':'FAIL',
            'error':'INVALID_FUNDRAISER',
            'message':'The fundraiser doesn\'t exist.'
        }
        return json_response(response)
    fundraiser = Initiative.objects.get(id = params['fundraiser'])
    # Check if user has logged in
    if user is not None:
        # If so, check if user has permission for the fundraiser
        if not Profile_manager.objects.filter(user = user, 
                                              profile = fundraiser.owner) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if (params['token'] is None or 
            fundraiser.access_token != params['token']):
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    # Check if the name is too long
    if len(params['name']) > 15:
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Reward name cannot be over 15 characters.'
        }
        return json_response(response)
    # Check if the description is too long
    if len(params['description']) > 150:
        response = {
            'status':'FAIL',
            'error':'INVALID_DESCRIPTION',
            'message':'Reward description cannot be over 150 characters.'
        }
        return json_response(response)
    # Check if the fundraiser has passed its deadline
    if fundraiser.is_launched and fundraiser.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'PAST_FUNDRAISER',
            'message':'You cannot add a reward to a past fundraiser.'
        }
        return json_response(response)
    # Check the price
    params['price'] = float(params['price'])
    if params['price'] <= 0:
        response = {
            'status':'FAIL',
            'error':'INVALID_PRICE',
            'message':'The price is invalid.'
        }
        return json_response(response)
    reward = Reward(fundraiser = fundraiser, 
                    name = params['name'], 
                    description = params['description'], 
                    price = params['price'])
    # Check the quantity
    if params['quantity'] is not None:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'The quantity is invalid.'
            }
            return json_response(response)
        else:
            reward.quantity = params['quantity']
    # All checks passed, write to database
    reward.save()
    response = {
        'status':'OK',
        'reward':serialize_one(reward)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], ['name', 'description', 'price', 'quantity', 'token'])
def edit_reward(request, params, user):
    """
    Edit a reward
    """
    # Check if reward is valid
    if not Reward.objects.filter(id = params['id']):
        response = {
            'status':'FAIL',
            'error':'INVALID_REWARD',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    reward = Reward.objects.get(id = params['id'])
    fundraiser = reward.fundraiser
    # Check if user has logged in
    if user is not None:
        # If so, check if user has permission for the fundraiser
        if not Profile_manager.objects.filter(user = user, 
                                              profile = fundraiser.owner) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if (params['token'] is None or 
            fundraiser.access_token != params['token']):
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    # Check if the deadline has passed
    if fundraiser.is_launched and fundraiser.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'DEADLINE_PAST_DUE',
            'message':'You cannot make changes to a past fundraiser'
        }
        return json_response(response)
    # Check if the reward is the reward of no price
    if reward.price == 0:
        response = {
            'status':'FAIL',
            'error':'FREE_REWARD',
            'message':'The free reward of the fundraiser cannot be edited.'
        }
        return json_response(response)
    # Go through all params and change the rewards accordingly
    if params['name'] is not None:
        if not (0 < len(params['name']) <= 15):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Reward name cannot be blank or over 15 characters.'
            }
            return json_response(response)
        else:
            reward.name = params['name']
    if params['description'] is not None:
        if not (0 < len(params['description']) <= 150):
            response = {
                'status':'FAIL',
                'error':'INVALID_DESCRIPTION',
                'message':'Reward description must be between 0-150 characters.'
            }
            return json_response(response)
        else:
            reward.description = params['description']
    if params['price'] is not None:
        params['price'] = float(params['price'])
        if params['price'] < 0:
            response = {
                'status':'FAIL',
                'error':'NEGATIVE_PRICE',
                'message':'Price cannot be a negative number.'
            }
            return json_response(response)
        else:
            reward.price = params['price']
    if params['quantity'] is not None:
        if params['quantity'].lower() == 'none':
            reward.quantity = None
        else:
            params['quantity'] = int(params['quantity'])
            if params['quantity'] <= 0:
                response = {
                    'status':'FAIL',
                    'error':'NON_POSITIVE_QUANTITY',
                    'message':'Quantity must be a positive integer.'
                }
                return json_response(response)
            else:
                reward.quantity = params['quantity']
    # Save the changes
    reward.save()
    response = {
        'status':'OK',
        'reward':serialize_one(reward)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], ['token'])
def delete_reward(request, params, user):
    """
    Delete a reward
    """
    # Check if reward is valid
    if not Reward.objects.filter(id = params['id']):
        response = {
            'status':'FAIL',
            'error':'INVALID_REWARD',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    reward = Reward.objects.get(id = params['id'])
    fundraiser = reward.fundraiser
    # Check if user has logged in
    if user is not None:
        # If so, check if user has permission for the fundraiser
        if not Profile_manager.objects.filter(user = user, 
                                              profile = fundraiser.owner) \
                                      .exists():
            response = {
                'status':'FAIL',
                'error':'NOT_A_MANAGER',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    else:
        # Otherwise check if the access token is valid
        if (params['token'] is None or 
            fundraiser.access_token != params['token']):
            response = {
                'status':'FAIL',
                'error':'PERMISSION_DENIED',
                'message':'You don\'t have permission for the fundraiser.'
            }
            return json_response(response)
    # Check if the deadline has passed
    if fundraiser.is_launched and fundraiser.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'DEADLINE_PAST_DUE',
            'message':'You cannot make changes to a past fundraiser'
        }
        return json_response(response)
    # Check if the reward is the reward of no price
    if reward.price == 0:
        response = {
            'status':'FAIL',
            'error':'FREE_REWARD',
            'message':'The free reward of the fundraiser cannot be deleted.'
        }
        return json_response(response)
    # Refund all pledges for the reward
    pledges = Pledge.objects.filter(reward = reward)
    for pledge in pledges:
        pass
    # Delete the reward
    reward.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@task()
def mark_donation_as_expired(donation):
    """
    Expires a donation after some time and release the reward
    """
    if not donation.checkout.is_captured:
        donation.is_expired = True
        donation.save()
        reward = donation.reward
        if reward.quantity is not None:
            reward.quantity = F('quantity') + 1
            reward.save()
    return True

@login_check()
@validate('POST', ['reward', 'amount'], ['email'])
def donate(request, params, user):
    """
    Donate for a reward
    """
    # Check login status
    if user is None:
        if params['email'] is None:
            response = {
                'status':'FAIL',
                'error':'MISSING_EMAIL',
                'message':'You need an email to purchase the ticket.'
            }
            return json_response(response)
        user, created = User.objects.get_or_create(email = params['email'])
        if not (user.password is None and user.fb_id is None):
            response = {
                'status':'FAIL',
                'error':'EMAIL_EXISTS',
                'message':'This email collides with an existing account.'
            }
            return json_response(response)
    # Check if the reward is valid
    if not Reward.objects.filter(id = params['reward']).exists():
        response = {
            'status':'FAIL',
            'error':'REWARD_NOT_FOUND',
            'message':'The reward doesn\'t exist.'
        }
        return json_response(response)
    reward = Reward.objects.get(id = params['reward'])
    fundraiser = reward.fundraiser
    # Check if the fundraiser is launched
    if not fundraiser.is_launched:
        response = {
            'status':'FAIL',
            'error':'FUNDRAISER_NOT_LAUNCHED',
            'message':'The fundraiser is not launched yet.'
        }
        return json_response(response)
    # Check if the fundraiser has reached its deadline
    if fundraiser.deadline <= timezone.now():
        response = {
            'status':'FAIL',
            'error':'DEADLINE_PAST_DUE',
            'message':'The fundraiser is closed.'
        }
        return json_response(response)
    # Check if the reward has run out
    if reward.quantity is not None and reward.quantity == 0:
        response = {
            'status':'FAIL',
            'error':'REWARD_RUN_OUT',
            'message':'This reward has run out.'
        }
        return json_response(response)
    # Check if there is an existing donation
    if Donation.objects.filter(owner = user, fundraiser = fundraiser, 
                               checkout__is_captured = True, 
                               checkout__is_cancelled = False, 
                               is_expired = False).exists():
        response = {
            'status':'FAIL',
            'error':'DONATED_ALREADY',
            'message':'You have donated for the fundraiser already.'
        }
        return json_response(response)
    # Check if the donation amount is non-zero and reaches the threshold
    params['amount'] = float(params['amount'])
    if params['amount'] == 0 or params['amount'] < reward.price:
        response = {
            'status':'FAIL',
            'error':'AMOUNT_NOT_VALID',
            'message':'Your donation amount is not valid for this reward.'
        }
        return json_response(response)
    # All checks passed, request a checkout on WePay
    checkoutDescription = fundraiser.name
    if len(reward.name) > 0:
        checkoutDescription += ' - ' + reward.name
    checkoutInfo = create_checkout('DONATION', fundraiser.owner.wepay_account, 
                                   checkoutDescription, params['amount'])
    checkout = Wepay_checkout(payer = user, 
                              payee = fundraiser.owner.wepay_account, 
                              checkout_id = checkoutInfo['checkout_id'], 
                              amount = params['amount'], 
                              description = checkoutDescription[:127])
    checkout.save()
    # Create the donation
    donation = Donation(owner = user, reward = reward, fundraiser = fundraiser, 
                        amount = params['amount'], checkout = checkout)
    donation.save()
    # Request a checkout on WePay
    checkout = create_checkout(donation)
    # If the reward has a quantity limit
    if reward.quantity is not None:
        # Schedule the donation to be expired after some amount of time
        expiration = timezone.now()
        expiration += timedelta(minutes = BBOY_TRANSACTION_EXPIRATION)
        mark_donation_as_expired.apply_async(args = [donation], 
                                             eta = expiration)
        # Adjust the reward quantity
        reward.quantity = F('quantity') - 1
        reward.save()
    response = {
        'status':'OK',
        'donation':serialize_one(donation),
        'checkout':serialize_one(checkout)
    }
    return json_response(response)