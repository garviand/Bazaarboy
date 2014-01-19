"""
Controller for sponsorships
"""

import cgi
from django.utils import timezone
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
@validate('POST', ['event', 'name', 'description'], 
          ['price_low', 'price_high', 'quantity'])
def create_criteria(request, params, user):
    """
    Create a criteria for sponsorship
    """
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    params['name'] = cgi.escape(params['name'])
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Criteria name must be within 50 characters.'
        }
        return json_response(response)
    params['description'] = cgi.escape(params['description'])
    criteria = Criteria(event = event, name = params['name'], 
                        description = params['description'])
    if params['price_low'] is not None:
        params['price_low'] = float(params['price_low'])
        if params['price_low'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_PRICE_RANGE',
                'message':'Price range is invalid.'
            }
            return json_response(response)
        else:
            criteria.price_low = params['price_low']
    if params['price_high'] is not None:
        params['price_high'] = float(params['price_high'])
        if params['price_high'] < 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_PRICE_RANGE',
                'message':'Price range is invalid.'
            }
            return json_response(response)
        else:
            criteria.price_high = params['price_high']
    if criteria.price_high is not None:
        if criteria.price_low is None:
            criteria.price_low = 0
        else:
            if criteria.price_low > criteria.price_high:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_PRICE_RANGE',
                    'message':'Price range is invalid.'
                }
                return json_response(response)
    if params['quantity'] is not None:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'Quantity is invalid.'
            }
            return json_response(response)
    criteria.save()
    response = {
        'status':'OK',
        'criteria':serialize_one(criteria)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'price_low', 'price_high', 'quantity'])
def edit_criteria(request, params, user):
    """
    Edit a criteria for sponsorship
    """
    if not Criteria.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CRITERIA_NOT_FOUND',
            'message':'The criteria doesn\'t exist.'
        }
        return json_response(response)
    criteria = Criteria.objects.get(id = params['id'])
    event = criteria.event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    if params['name'] is not None:
        params['name'] = cgi.escape(params['name'])
        if len(params['name']) > 50:
            response = {
                'status':'FAIL',
                'error':'NAME_TOO_LONG',
                'message':'Criteria name must be under 50 characters.'
            }
            return json_response(response)
        else:
            criteria.name = params['name']
    if params['description'] is not None:
        params['description'] = cgi.escape(params['description'])
        if len(params['description']) > 150:
            response = {
                'status':'FAIL',
                'error':'DESCRIPTION_TOO_LONG',
                'message':'Criteria description must be under 150 characters.'
            }
            return json_response(response)
        else:
            criteria.description = params['description']
    if params['price_low'] is not None:
        if params['price_low'] == 'none':
            criteria.price_low = None
        else:
            params['price_low'] = float(params['price_low'])
            if params['price_low'] < 0:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_PRICE_RANGE',
                    'message':'Price range is invalid.'
                }
                return json_response(response)
            else:
                criteria.price_low = params['price_low']
    if params['price_high'] is not None:
        if params['price_high'] == 'none':
            criteria.price_high = None
        else:
            params['price_high'] = float(params['price_high'])
            if params['price_high'] < 0:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_PRICE_RANGE',
                    'message':'Price range is invalid.'
                }
                return json_response(response)
            else:
                criteria.price_high = params['price_high']
    if criteria.price_high is not None:
        if criteria.price_low is None:
            criteria.price_low = 0
        else:
            if criteria.price_low > criteria.price_high:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_PRICE_RANGE',
                    'message':'Price range is invalid.'
                }
                return json_response(response)
    if params['quantity'] is not None:
        if params['quantity'].lower() == 'none':
            criteria.quantity = None
        else:
            params['quantity'] = int(params['quantity'])
            if params['quantity'] <= 0:
                response = {
                    'status':'FAIL',
                    'error':'INVALID_QUANTITY',
                    'message':'Quantity is invalid.'
                }
                return json_response(response)
            else:
                criteria.quantity = params['quantity']
    criteria.save()
    response = {
        'status':'OK',
        'criteria':serialize_one(criteria)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete_criteria(request, params, user):
    """
    Delete a criteria for a sponsorship
    """
    if not Criteria.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CRITERIA_NOT_FOUND',
            'message':'The criteria doesn\'t exist.'
        }
        return json_response(response)
    criteria = Criteria.objects.get(id = params['id'])
    event = criteria.event
    if not Event_organizer.objects.filter(event = event, 
                                          profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    criteria.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['event'], ['profile', 'name', 'description', 'image'])
def create(request, params, user):
    """
    Create a sponsorship
    """
    if not Event.objects.filter(id = params['event'], 
                                is_deleted = False).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    event = Event.objects.get(id = params['event'])
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    profile = None
    if params['profile'] is not None:
        # Existing profile
        if not Profile.objects.filter(id = params['profile']).exists():
            response = {
                'status':'FAIL',
                'error':'PROFILE_NOT_FOUND',
                'message':'The profile doesn\'t exist.'
            }
            return json_response(response)
        profile = Profile.objects.get(id = params['profile'])
    name = None
    description = None
    image = None
    if params['name'] is not None:
         params['name'] = cgi.escape(params['name'])
         if not (0 < len(params['name']) <= 100):
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'The name must be within 100 characters.'
            }
            return json_response(response)
        name = params['name']
    if params['description'] is not None:
         params['description'] = cgi.escape(params['description'])
         if not (0 < len(params['description']) <= 500):
            response = {
                'status':'FAIL',
                'error':'INVALID_DESCRIPTION',
                'message':'The description must be within 500 characters.'
            }
            return json_response(response)
        description = params['description']
    if params['image'] is not None:
        if not Image.objects.filter(id = params['image']).exists():
            response = {
                'status':'FAIL',
                'error':'IMAGE_NOT_FOUND',
                'message':'The image doesn\'t exist.'
            }
            return json_response(response)
        else:
            image = Image.objects.get(id = params['image'])
            image.is_archived = True
            image.save()
    if profile is not None:
        name = profile.name
        description = '' if description is None else description
        image = None if image is None else profile.image
    if profile is None and name is None:
        response = {
            'status':'FAIL',
            'error':'INCOMPLETE_INFO',
            'message':'You must provide the name for the sponsor!'
        }
        return json_response(response)
    sponsorship = Sponsorship(owner = profile, event = event, name = name, 
                              description = description, image = image)
    sponsorship.save()
    response = {
        'status':'OK', 
        'sponsorship':serialize_one(sponsorship)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete(request, params, user):
    """
    Delete a sponsorship
    """
    if not Sponsorship.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'SPONSORSHIP_NOT_FOUND',
            'message':'The sponsorship doesn\'t exist.'
        }
        return json_response(response)
    sponsorship = Sponsorship.objects.get(id = params['id'])
    event = sponsorship.event
    if not Organizer.objects.filter(event = event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    sponsorship.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)