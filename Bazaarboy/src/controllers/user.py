"""
Controller for all user related actions
"""

import hashlib
from kernel.models import *
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from src.regex import REGEX_EMAIL
from src.serializer import serialize_one
from request import json_response, validate

@validate('GET', [], ['next'])
def register(request, params):
    """
    Register page
    An optional parameter 'next' is taken to denote a redirect after action.
    """
    if request.session.has_key('user'):
        # Session already exists, redirect to index
        return redirect('index')
    return render(request, 'register.html', locals())

@validate('POST', ['email', 'password', 'confirm', 'city'])
def create(request, params):
    """
    Create a new user
    """
    # Check if session exists
    if request.session.has_key('user'):
        return HttpResponseForbidden('Access forbidden.')
    # Check if the email exists
    if User.objects.filter(email = params['email']).exists():
        response = {
            'status':'FAIL',
            'error':'DUPLICATE_EMAIL',
            'message':'This email has already been registered.'
        }
        return json_response(response)
    # Check email format
    if not REGEX_EMAIL.match(params['email']):
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
    if params['confirm'] != params['password']:
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
    sessionUser = serialize_one(user, ('id', 'email', 'fb_id', 'city', 
                                       'created_time'))
    request.session['user'] = sessionUser
    response = {
        'status':'OK'
    }
    return json_response(response)

@validate('GET', [], ['next'])
def login(request, params):
    """
    Login page
    An optional parameter 'next' is taken to denote a redirect after action.
    """
    if request.session.has_key('user'):
        # Session already exists, redirect to index
        return redirect('index')
    return render(request, 'login.html', locals())

@validate('POST', ['email', 'password'])
def auth(request, params):
    """
    Authenticate a user
    """
    # Check if session exists
    if request.session.has_key('user'):
        return HttpResponseForbidden('Access forbidden.')
    # Authenticate email and password combination
    if User.objects.filter(email = params['email']).exists():
        user = User.objects.get(email = params['email'])
        saltedPassword = user.salt + params['password']
        if user.password == hashlib.sha512(saltedPassword).hexdigest():
            # Email and password match, start session
            sessionUser = serialize_one(user, ('id', 'email', 'fb_id', 
                                               'city', 'created_time'))
            request.session['user'] = sessionUser
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

def logout(request):
    request.session.flush()
    response = {
        'status':'OK'
    }
    return json_response(response)
