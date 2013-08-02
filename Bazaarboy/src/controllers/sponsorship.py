"""
Controller for sponsorships
"""

from django.utils import timezone
from kernel.models import *
from src.controllers.request import *
from src.controllers.wepay import create_checkout
from src.serializer import serialize_one

def SponsorshipFactory(eventType):
    """
    Return the correct models based on event type
    """
    EventModel, CriteriaModel, SponsorshipModel = None, None, None
    if eventType.lower() == 'event':
        EventModel = Event
        CriteriaModel = Event_criteria
        SponsorshipModel = Event_sponsorship
    elif eventType.lower() == 'fundraiser':
        EventModel = Fundraiser
        CriteriaModel = Fundraiser_criteria
        SponsorshipModel = Fundraiser_sponsorship
    return EventModel, CriteriaModel, SponsorshipModel

def isValidEvent(event, eventType):
    """
    Check if the event is a past event
    """
    if event.is_launched:
        if eventType.lower() == 'event':
            return event.start_time > timezone.now()
        elif eventType.lower() == 'fundraiser':
            return event.deadline > timezone.now()
    return True

@login_required()
@validate('POST', ['type', 'for', 'name', 'description', 'price'], 
          ['quantity'])
def create(request, params, user):
    """
    Create a criteria for sponsorship
    """
    models = SponsorshipFactory(params['type'])
    if None in models:
        response = {
            'status':'FAIL',
            'error':'INVALID_EVENT_TYPE',
            'message':'The event type is invalid.'
        }
        return json_response(response)
    EventModel, CriteriaModel, SponsorshipModel = models
    if not EventModel.objects.filter(id = params['for']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event doesn\'t exist.'
        }
        return json_response(response)
    _for = EventModel.objects.get(id = params['for'])
    if not isValidEvent(_for, params['type']):
        response = {
            'status':'FAIL',
            'error':'PAST_EVENT',
            'message':'You cannot modify a past event.'
        }
        return json_response(response)
    if len(params['name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Criteria name cannot be over 50 characters.'
        }
        return json_response(response)
    if len(params['description']) > 150:
        response = {
            'status':'FAIL',
            'error':'DESCRIPTION_TOO_LONG',
            'message':'Criteria description must be under 150 characters.'
        }
        return json_response(response)
    params['price'] = float(params['price'])
    if params['price'] <= 0:
        response = {
            'status':'FAIL',
            'error':'INVALID_PRICE',
            'message':'Price is invalid.'
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
    criteria = CriteriaModel(name = params['name'], 
                             description = params['description'], 
                             price = params['price'], 
                             quantity = params['quantity'], 
                             _for = _for)
    criteria.save()
    response = {
        'status':'OK',
        'criteria':serialize_one(criteria)
    }
    return json_response(response)

@login_required()
@validate('POST', ['type', 'id'], ['name', 'description', 'price', 'quantity'])
def edit(request, params, user):
    """
    Edit a criteria for sponsorship
    """
    models = SponsorshipFactory(params['type'])
    if None in models:
        response = {
            'status':'FAIL',
            'error':'INVALID_EVENT_TYPE',
            'message':'The event type is invalid.'
        }
        return json_response(response)
    EventModel, CriteriaModel, SponsorshipModel = models
    if not CriteriaModel.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CRITERIA_NOT_FOUND',
            'message':'The criteria doesn\'t exist.'
        }
        return json_response(response)
    criteria = CriteriaModel.objects.get(id = params['id'])
    if not isValidEvent(criteria._for, params['type']):
        response = {
            'status':'FAIL',
            'error':'PAST_EVENT',
            'message':'You cannot modify a past event.'
        }
        return json_response(response)
    if params['name'] is not None:
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
        if len(params['description']) > 150:
            response = {
                'status':'FAIL',
                'error':'DESCRIPTION_TOO_LONG',
                'message':'Criteria description must be under 150 characters.'
            }
            return json_response(response)
        else:
            criteria.description = params['description']
    if params['price'] is not None:
        params['price'] = float(params['price'])
        if params['price'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_PRICE',
                'message':'Price is invalid.'
            }
            return json_response(response)
        else:
            criteria.price = params['price']
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
@validate('POST', ['type', 'id'])
def delete(request, params, user):
    """
    Delete a criteria for a sponsorship
    """
    models = SponsorshipFactory(params['type'])
    if None in models:
        response = {
            'status':'FAIL',
            'error':'INVALID_EVENT_TYPE',
            'message':'The event type is invalid.'
        }
        return json_response(response)
    EventModel, CriteriaModel, SponsorshipModel = models
    if not CriteriaModel.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CRITERIA_NOT_FOUND',
            'message':'The criteria doesn\'t exist.'
        }
        return json_response(response)
    criteria = CriteriaModel.objects.get(id = params['id'])
    if not isValidEvent(criteria._for, params['type']):
        response = {
            'status':'FAIL',
            'error':'PAST_EVENT',
            'message':'You cannot modify a past event.'
        }
        return json_response(response)
    if SponsorshipModel.objects.filter(criteria = criteria, 
                                       checkout__is_captured = True, 
                                       checkout__is_refunded = False) \
                               .exists():
        response = {
            'status':'FAIL',
            'error':'EXISTING_SPONSORSHIP',
            'message':'There is an existing sponsorship with this criteria.'
        }
        return json_response(response)
    criteria.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['type', 'criteria', 'profile', 'amount'])
def sponsor(request, params, user):
    """
    Sponsor for an event
    """
    models = SponsorshipFactory(params['type'])
    if None in models:
        response = {
            'status':'FAIL',
            'error':'INVALID_EVENT_TYPE',
            'message':'The event type is invalid.'
        }
        return json_response(response)
    EventModel, CriteriaModel, SponsorshipModel = models
    if not CriteriaModel.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'CRITERIA_NOT_FOUND',
            'message':'The criteria doesn\'t exist.'
        }
        return json_response(response)
    criteria = CriteriaModel.objects.get(id = params['id'])
    if not isValidEvent(criteria._for, params['type']):
        response = {
            'status':'FAIL',
            'error':'PAST_EVENT',
            'message':'You cannot sponsor a past event.'
        }
        return json_response(response)
    params['amount'] = float(params['amount'])
    if params['amount'] < criteria.price:
        response = {
            'status':'FAIL',
            'error':'NOT_ENOUGH',
            'message':'Your sponsorship does not meet the criteria price.'
        }
        return json_response(response)
    if criteria.quantity is not None and criteria.quantity == 0:
        response = {
            'status':'FAIL',
            'error':'NO_MORE_SPOTS',
            'message':'The criteria of sponsorship has run out.'
        }
        return json_response(response)
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
    checkoutType = 'EVENT' if params['type'].lower() == 'event' else 'DONATION'
    checkoutDescription = '%s - Sponsorship %s' % (criteria._for.name, 
                                                   criteria.name)
    checkoutInfo = create_checkout(checkoutType, 
                                   criteria._for.owner.wepay_account.account_id, 
                                   checkoutDescription, params['amount'])
    sponsorship = SponsorshipModel(owner = profile, criteria = criteria, 
                                   _for = criteria._for, 
                                   amount = params['amount'], 
                                   checkout_id = checkoutInfo['checkout_id'])
    sponsorship.save()
    response = {
        'status':'OK',
        'sponsorship':serialize_one(sponsorship)
    }
    return json_response(response)