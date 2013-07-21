"""
Controller for all user related actions
"""

import hashlib
import os
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone
from facebook import GraphAPI, GraphAPIError
from kernel.models import *
from src.controllers.request import json_response, validate, login_check
from src.email import Email
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
@validate('GET', [], ['next'])
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
@validate('GET', [], ['code'])
def reset(request, params, loggedIn):
    """
    Reset password page
    """
    if loggedIn:
        pass
    pass

@login_check()
@validate('POST', 
          ['email', 'password', 'confirm', 'first_name', 'last_name', 'city'])
def create(request, params, loggedIn):
    """
    Create a new user using email and password
    """
    # Check if session exists
    if loggedIn:
        return HttpResponseForbidden('Access forbidden.')
    # Check if the email has already been registered
    if User.objects.filter(Q(password = None) | Q(fb_id = None), 
                           email = params['email']).exists():
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
            'message':'The confirm password does not match the original one.'
        }
        return json_response(response)
    # Check if the name is valid
    if len(params['first_name']) > 30 or len(params['last_name']) > 30:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Your first/last name is too long.'
        }
        return json_response(response)
    # Find the unactivated user, or create a new one
    user = User(email = params['email'])
    if User.objects.filter(email = params['email']).exists():
        user = User.objects.get(email = params['email'])
    # Set the user information
    user.password = params['password']
    user.first_name = params['first_name']
    user.last_name = params['last_name']
    user.save()
    # Creation done, send out a confirmation email
    # Start the session
    request.session['user'] = user.id
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('GET', ['email', 'password'])
def auth(request, params, loggedIn):
    """
    Authenticate a user using email and password
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

@login_check()
@validate('POST', ['fb_token'], ['email'])
def fbAuth(request, params, loggedIn):
    """
    Authenticate or create a user using a Facebook account
    """
    # Check if session exists
    if loggedIn:
        return HttpResponseForbidden('Access forbidden.')
    # Verify the access token by trying to get the profile information
    fbClient = GraphAPI(params['fb_token'])
    try:
        fbProfile = fbClient.get_object('me')
    except GraphAPIError as error:
        response = {
            'status':'FAIL',
            'message':error.message
        }
        return json_response(response)
    else:
        if User.objects.filter(fb_id = fbProfile['id']).exists():
            # Account linked to the Facebook ID exists, start session
            user = User.objects.get(fb_id = fbProfile['id'])
            request.session['user'] = user.id
            response = {
                'status':'OK'
            }
            return json_response(response)
        else:
            # No record exists, attempt to create the user
            # Check email format
            if (params['email'] is None or 
                not REGEX_EMAIL.match(params['email'])):
                response = {
                    'status':'FAIL',
                    'error':'INVALID_EMAIL',
                    'message':'Email format is invalid.'
                }
                return json_response(response)
            # Check if the email has already been registered
            if User.objects.filter(Q(password = None) | Q(fb_id = None), 
                                   email = params['email']).exists():
                response = {
                    'status':'FAIL',
                    'error':'DUPLICATE_EMAIL',
                    'message':'This email has already been registered.'
                }
                return json_response(response)
            # Find the unactivated user, or create a new one
            user = User(email = params['email'])
            if User.objects.filter(email = params['email']).exists():
                user = User.objects.get(email = params['email'])
            user.fb_id = fbProfile['id']
            user.fb_access_token = params['fb_token']
            user.first_name = fbProfile['first_name'][:35]
            user.last_name = fbProfile['last_name'][:35]
            user.save()
            # Creation done, send out confirmation email
            code = os.urandom(128).encode('base_64')[:128]
            confirmationCode = User_confirmation_code(user = user, code = code)
            email = Email()
            email.sendConfirmationEmail(confirmationCode)
            # Start the session
            request.session['user'] = user.id
            response = {
                'status':'OK'
            }
            return json_response(response)

@login_check()
@validate('POST', ['email'])
def create_reset(request, params, loggedIn):
    """
    Create a request for password reset
    """
    # Check if session exists
    if loggedIn:
        return HttpResponseForbidden('Access forbidden.')
    # Check if account exists
    if not User.objects.filter(Q(password = None) | Q(fb_id = None), 
                               email = params['email']).exists():
        response = {
            'status':'FAIL',
            'message':'The email has not been registered yet.'
        }
        return json_response(response)
    user = User.objects.get(email = params['email'])
    expirationTime = timezone.now() + timedelta(days = 3)
    resetCode = User_reset_code(user = user, 
                           code = os.urandom(128).encode('base_64')[:128], 
                           expiration_time = expirationTime)
    resetCode.save()
    email = Email()
    email.sendResetRequestEmail(resetCode)
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('POST', ['password', 'confirm'], ['code'])
def chnage_password(request, params, loggedIn):
    """
    Change the password of a user
    """
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
            'message':'The confirm password does not match the original one.'
        }
        return json_response(response)
    # Get the user from session or using a reset code
    user = User.objects.get(id = request.session['user']) if loggedIn else None
    if user is None:
        if (params['code'] is None or 
            not User_reset_code.objects.filter(code = params['code']).exists()):
            response = {
                'status':'FAIL',
                'error':'INVALID_CODE',
                'message':'The reset code is invalid.'
            }
            return json_response(response)
        resetCode = User_reset_code.objects.get(code = params['code'])
        if resetCode.expiration_time <= timezone.now():
            resetCode.is_expired = True
        if resetCode.is_expired:
            resetCode.save()
            response = {
                'status':'FAIL',
                'error':'EXPIRED_CODE',
                'message':'The code is expired.'
            }
            return json_response(response)
        resetCode.is_expired = True
        resetCode.save()
        user = resetCode.user
    # Checks passed, change the password
    user.password = params['password']
    user.save()
    # Send a notification email to the user
    email = Email()
    email.sendPasswordChangedEmail(user)
    response = {
        'status':'OK'
    }
    return json_response(response)

def logout(request):
    """
    Log out the user
    """
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