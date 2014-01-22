"""
Controller for bonuses
"""

import cgi
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_required()
@validate('POST', 
          ['event', 'name', 'description'], 
          ['image', 'quantity', 'code', 'expiration_time'])
def create(request, params, user):
    """
    Create bonus
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
    if len(params['description']) > 150:
        response = {
          'status':'FAIL',
          'error':'DESCRIPTION_TOO_LONG',
          'message':'The description must be within 150 characters.'
        }
        return json_response(response)
    bonus = Bonus(event = event, name = params['name'], 
                  description = params['description'])
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
            bonus.image = image
    if params['quantity'] is not None:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'Quantity must be a positive number.'
            }
            return json_response(response)
        else:
            bonus.quantity = params['quantity']
    if params['code'] is not None:
        params['code'] = cgi.escape(params['code'])
        if len(params['code']) > 255:
            response = {
                'status':'FAIL',
                'error':'INVALID_CODE',
                'message':'The code must be within 255 characters.'
            }
            return json_response(response)
        else:
            bonus.code = params['code']
    if params['expiration_time'] is not None:
        if params['expiration_time'] <= timezone.now():
            response = {
                'status':'FAIL',
                'error':'EXPIRED_ALREADY',
                'message':'The expiration time is past due.'
            }
            return json_response(response)
        else:
            bonus.expiration_time = params['expiration_time']
    bonus.save()
    response = {
        'status':'OK',
        'bonus':serialize_one(bonus)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'], 
          ['name', 'description', 'image', 'quantity', 'code', 
           'expiration_time'])
def edit(request, params, user):
    """
    Edit a bonus
    """
    if not Bonus.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'BONUS_NOT_FOUND',
            'message':'The bonus doesn\'t exist.'
        }
        return json_response(response)
    bonus = Bonus.objects.get(id = params['id'])
    if not Organizer.objects.filter(event = bonus.event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the bonus.'
        }
        return json_response(response)
    if bonus.is_sent:
        response = {
            'status':'FAIL',
            'error':'READ_ONLY',
            'message':'You cannot make changes to a sent bonus.'
        }
        return json_response(response)
    if params['name'] is not None:
        params['name'] = cgi.escape(params['name'])
        if not (0 < len(params['name']) <= 50):
            response = {
                'status':'FAIL',
                'error':'NAME_TOO_LONG',
                'message':'Criteria name must be within 50 characters.'
            }
            return json_response(response)
        else:
            bonus.name = params['name']
    if params['description'] is not None:
        params['description'] = cgi.escape(params['description'])
        if not (0 < len(params['description']) <= 150):
            response = {
              'status':'FAIL',
              'error':'DESCRIPTION_TOO_LONG',
              'message':'The description must be within 150 characters.'
            }
            return json_response(response)
        else:
            bonus.description = params['description']
    if params['image'] is not None:
        if params['image'] == 'none':
            if bonus.image is not None:
                oldImage = Image.objects.get(id = bonus.image.id)
                oldImage.delete()
                bonus.image = None
        elif not Image.objects.filter(id = params['image']).exists():
            response = {
                'status':'FAIL',
                'error':'IMAGE_NOT_FOUND',
                'message':'The image doesn\'t exist.'
            }
            return json_response(response)
        else:
            image = Image.objects.get(id = params['image'])
            if bonus.image is not None:
                oldImage = Image.objects.get(id = bonus.image.id)
                oldImage.delete()
            image.is_archived = True
            image.save()
            bonus.image = image
    if params['quantity'] is not None:
        params['quantity'] = int(params['quantity'])
        if params['quantity'] <= 0:
            response = {
                'status':'FAIL',
                'error':'INVALID_QUANTITY',
                'message':'Quantity must be a positive number.'
            }
            return json_response(response)
        else:
            bonus.quantity = params['quantity']
    if params['code'] is not None:
        params['code'] = cgi.escape(params['code'])
        if len(params['code']) > 255:
            response = {
                'status':'FAIL',
                'error':'INVALID_CODE',
                'message':'The code must be within 255 characters.'
            }
            return json_response(response)
        else:
            bonus.code = params['code']
    if params['expiration_time'] is not None:
        if params['expiration_time'] <= timezone.now():
            response = {
                'status':'FAIL',
                'error':'EXPIRED_ALREADY',
                'message':'The expiration time is past due.'
            }
            return json_response(response)
        else:
            bonus.expiration_time = params['expiration_time']
    bonus.save()
    response = {
        'status':'OK',
        'bonus':serialize_one(bonus)
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def delete(request, params, user):
    """
    Delete a bonus
    """
    if not Bonus.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'BONUS_NOT_FOUND',
            'message':'The bonus doesn\'t exist.'
        }
        return json_response(response)
    bonus = Bonus.objects.get(id = params['id'])
    if not Organizer.objects.filter(event = bonus.event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the bonus.'
        }
        return json_response(response)
    if bonus.is_sent:
        response = {
            'status':'FAIL',
            'error':'READ_ONLY',
            'message':'You cannot delete a sent bonus.'
        }
        return json_response(response)
    bonus.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_required()
@validate('POST', ['id'])
def send(request, params, user):
    """
    Send out bonus to users
    """
    pass

@validate('POST', ['id', 'token'])
def claim(request, params):
    """
    Claim a bonus
    """
    pass