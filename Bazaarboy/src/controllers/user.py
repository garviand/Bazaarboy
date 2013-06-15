"""
Controller for all user related actions
"""

import hashlib
import re
from kernel.models import User
from request import json_response, validate
from src.regex import REGEX_EMAIL

@validate('POST', ['email', 'password', 'confirm', 'city'])
def create(request, params):
    """
    Create a new user
    """
    # Check if the email exists
    if User.objects.filter(email = params['email']).exists():
        response = {
            'status':'FAIL',
            'error':'DUPLICATE_EMAIL',
            'message':'This email has already been registered.'
        }
        return json_response(response)
    # Check email format
    if not re.search(REGEX_EMAIL, params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    # Check password format
    if not 6 <= len(params['password']) <= 16:
        response = {
            'status':'FAIL',
            'error':'INVALID_PASSWORD',
            'message':'The length of password is invalid.'
        }
        return json_response(response)
    # Check confirm password
    if params['confirm'] != password['password']:
        response = {
            'status':'FAIL',
            'error':'PASSWORDS_MISMATCH',
            'message':'The confirm password does not match the original one'
        }
        return json_response(response)
    # Check if the city exists
    if not City.objects.filter(id = params['city']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city does not exist.'
        }
        return json_response(response)
    # Create the user
    city = City.objects.get(id = params['city'])
    user = User(email = params['email'], 
                password = params['password'], 
                city = city)
    user.save()
    # Creation done, start session
    response = {
        'status':'OK'
    }
    return json_response(response)

@validate('GET', ['email', 'password'])
def login(request, params):
    """
    Login verification
    """
    if User.objects.filter(email = params['email']).exists():
        user = User.objects.get(email = params['email'])
        saltedPassword = user.salt + params['password']
        if user.password == hashlib.sha512(saltedPassword).hexdigest():
            # Email and password match, start session
            response = {
                'status':'OK'
            }
            return json_response(response)
    # Validation failed
    response = {
        'status':'FAIL',
        'message':'Invalid email or password.'
    }
    return json_response(response)