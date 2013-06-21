"""
Controller for all user related actions
"""

import hashlib
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from kernel.models import *
from src.controllers.request import json_response, validate, login_check
from src.regex import REGEX_EMAIL
from src.serializer import serialize_one

@login_check()
@validate('GET', [], ['next'])
def register(request, params, loggedIn):
    """
    Register page
    An optional parameter 'next' is taken to denote a redirect after action.
    """
    if loggedIn:
        # Session already exists, redirect to index
        return redirect('index')
    return render(request, 'register.html', locals())

@login_check()
@validate('POST', ['email', 'password', 'confirm', 'city'])
def create(request, params, loggedIn):
    """
    Create a new user
    """
    # Check if session exists
    if loggedIn:
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
            'message':'The city doesn\'t exist.'
        }
        return json_response(response)
    # Create the user
    city = City.objects.get(id = params['city'])
    user = User(email = params['email'], 
                password = params['password'], 
                city = city)
    user.save()
    # Creation done, start session
    request.session['user'] = user.id
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('GET')
def login(request, params, loggedIn):
    """
    Login page
    An optional parameter 'next' is taken to denote a redirect after action.
    """
    if loggedIn:
        # Session already exists, redirect to index
        return redirect('index')
    return render(request, 'login.html', locals())

@login_check()
@validate('GET', ['email', 'password'])
def auth(request, params, loggedIn):
    """
    Authenticate a user
    """
    # Check if session exists
    if loggedIn:
        return HttpResponseForbidden('Access forbidden.')
    # Authenticate email and password combination
    if User.objects.filter(email = params['email']).exists():
        user = User.objects.get(email = params['email'])
        saltedPassword = user.salt + params['password']
        if user.password == hashlib.sha512(saltedPassword).hexdigest():
            # Email and password match, start session
            request.session['user'] = user.id
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
    # Preserve the admin session if exists
    adminSession = None
    if request.session.has_key('admin'):
        adminSession = request.session['admin']
    # Clear the current session
    request.session.flush()
    # Restore the admin session if exists
    if adminSession is not None:
        request.session['admin'] = adminSession
    return redirect('index')