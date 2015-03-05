"""
Controller for all user related actions
"""

import hashlib
import uuid
import os
import random
import cgi
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone
from facebook import GraphAPI, GraphAPIError
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.email import sendConfirmationEmail, sendResetRequestEmail, sendNewAccountEmail
from src.regex import REGEX_EMAIL, REGEX_NAME
from src.serializer import serialize_one

import pdb

@validate('GET', ['key', 'email'], ['profile'])
def unsubscribe(request, params):
    """
    Unsubscribe from Invites and Follow-Ups
    """
    check_key = hashlib.sha512(params['email'] + UNSUBSCRIBE_SALT).hexdigest()
    if params['profile']:
        profileCheck = params['profile']
    else:
        profileCheck = 0
    if params['key'] == check_key:
        if not Unsubscribe.objects.filter(Q(email = params['email']), Q(profile__id = profileCheck) | Q(profile__isnull = True)).exists():
            unsubscribe = Unsubscribe(email = params['email'])
            if params['profile'] is not None and Profile.objects.filter(id = params['profile']).exists():
                profile = Profile.objects.get(id = params['profile'])
                unsubscribe.profile = profile
            unsubscribe.save()
            message = 'You have succesfully unsubscribed. You will still receive confirmation emails if you RSVP for an event.'
            return render(request, 'user/unsubscribe.html', locals())
        else:
            message = 'You have already unsubscribed from this email.'
            return render(request, 'user/unsubscribe.html', locals())
    else:
        message = 'The email you are using cannot be verified, please contact us at build@bazaarboy.com.'
        return render(request, 'user/unsubscribe.html', locals())

@login_check()
@validate('GET')
def register(request, params, user):
    """
    Register page
    """
    if user is not None:
        # Session already exists, redirect to index
        return redirect('index')
    orgInfo = request.GET.dict()
    return render(request, 'user/register.html', locals())

@login_check()
@validate('GET')
def login(request, params, user):
    """
    Login page
    """
    if user is not None:
        # Session already exists, redirect to index
        return redirect('index')
    return render(request, 'user/login.html', locals())

@login_check()
@validate('GET', ['code'])
def confirm(request, params, user):
    """
    Confirm email page
    """
    if not User_confirmation_code.objects.filter(code = params['code']) \
                                         .exists():
        return HttpResponseForbidden('Access forbidden.')
    confirmationCode = User_confirmation_code.objects.get(code = params['code'])
    _user = confirmationCode.user
    _user.is_confirmed = True
    _user.save()
    confirmationCode.delete()
    if user is not None:
        return redirect('index')
    return redirect('user:login')

@login_check()
@validate('GET', [], ['code'])
def reset(request, params, user):
    """
    Reset password page
    """
    if user is not None:
        # Logged in user should use their account settings to change password
        return redirect('index')
    if params['code'] is not None:
        # If a code is passed, check if it's valid
        isCodeValid = True
        if not User_reset_code.objects.filter(code = params['code']).exists():
            isCodeValid = False
        else:
            resetCode = User_reset_code.objects.get(code = params['code'])
            if resetCode.expiration_time <= timezone.now():
                resetCode.is_expired = True
                resetCode.save()
            isCodeValid = not resetCode.is_expired
        # Render the page to reset the password
        return render(request, 'user/reset.html', locals())
    # No code is passed, render the page to send a reset request
    return render(request, 'user/reset.html', locals())

@login_required()
def settings(request, user):
    """
    User settings page
    """
    stripeConnectUrl = r'%s?response_type=code&client_id=%s&scope=%s'
    stripeConnectUrl = stripeConnectUrl % (STRIPE_CONNECT_URL, 
                                           STRIPE_CLIENT_ID, 
                                           STRIPE_SCOPE)
    profiles = Profile.objects.filter(managers = user)
    profile = profiles[0]
    return render(request, 'user/settings.html', locals())

@login_check()
@validate('POST', ['email', 'password', 'first_name', 'last_name'], ['request_id', 'request_code', 'reward_id', 'reward_token', 'organization_name', 'logo_id'])
def create(request, params, user):
    """
    Create a new user using email and password
    """
    # Check if session exists
    if user is not None:
        return HttpResponseForbidden('Access forbidden.')
    # Check if the email has already been registered
    if User.objects.filter(email = params['email'], password__isnull = False) \
                   .exists():
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
    # Check if the name is valid
    if (not REGEX_NAME.match(params['first_name']) or 
        not REGEX_NAME.match(params['last_name'])):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Your first or last name contain illegal characters.'
        }
        return json_response(response)
    if len(params['first_name']) > 50 or len(params['last_name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Your first or last name is too long.'
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
    if Collaboration_request.objects.filter(id = params['request_id'], code = params['request_code'], profile__isnull = True, user__isnull = True).exists():
        collaboration = Collaboration_request.objects.get(id = params['request_id'])
        collaboration.user = user
        collaboration.save()
    # Creation done, send out a confirmation email
    code = os.urandom(128).encode('base_64')[:128]
    confirmationCode = User_confirmation_code(user = user, code = code)
    confirmationCode.save()
    if params['organization_name'] is not None:
        params['organization_name'] = cgi.escape(params['organization_name'])
        if len(params['organization_name']) > 100:
            response = {
                'status':'FAIL',
                'error':'INVALID_NAME',
                'message':'Profile name cannot be over 100 characters.'
            }
            return json_response(response)
        profile = Profile(name = params['organization_name'], description = params['organization_name'], location = ' ', email = params['email'])
        if params['logo_id'] is not None and params['logo_id'].strip() != '':
            if Image.objects.filter(id = params['logo_id']).exists():
                profile.image = Image.objects.get(id = params['logo_id'])
        profile.save()
        if Collaboration_request.objects.filter(user = user, profile__isnull = True).exists():
            collaboration_requests = Collaboration_request.objects.filter(user = user, profile__isnull = True)
            for collab in collaboration_requests:
                collab.profile = profile
                collab.save()
        profileManager = Profile_manager(user = user,
                                         profile = profile,
                                         is_creator = True)
        profileManager.save()
        #sendNewAccountEmail(profile)
        if params['reward_id'] is not None and params['reward_token'] is not None:
            if Reward_send.objects.filter(id = params['reward_id'], token = params['reward_token']).exists():
                reward_send = Reward_send.objects.get(id = params['reward_id'])
                if reward_send.expiration_time < timezone.now():
                    response = {
                        'status':'FAIL',
                        'message':'This gift has already expired.'
                    }
                    return json_response(response)
                if reward_send.claimed:
                    response = {
                        'status':'FAIL',
                        'message':'This gift has already been claimed.'
                    }
                    return json_response(response)
                reward_item = Reward_item(reward = reward_send.reward, owner = profile, quantity = reward_send.quantity, expiration_time = reward_send.expiration_time)
                reward_item.save()
                reward_send.claimed = True
                reward_send.save()
                request.session['user'] = user.id
                response = {
                    'status':'REWARD'
                }
                return json_response(response)
    request.session['user'] = user.id
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('POST', ['email', 'password'], ['request_id', 'request_code', 'reward_id', 'reward_token'])
def auth(request, params, user):
    """
    Authenticate a user using email and password
    """
    # Check if session exists
    if user is not None:
        return HttpResponseForbidden('Access forbidden.')
    # Authenticate email and password combination
    if User.objects.filter(email = params['email']).exists():
        user = User.objects.get(email = params['email'])
        if user.password is None:
            response = {
                'status':'FAIL',
                'message':'There is no account associated with this email.'
            }
            return json_response(response)
        saltedPassword = user.salt + params['password']
        if user.password == hashlib.sha512(saltedPassword).hexdigest():
            # Check if the account is active
            if not user.is_active:
                response = {
                    'status':'FAIL',
                    'message':'Your account is not active, please contact us.'
                }
                return json_response(response)
            # Email and password match, start session
            request.session['user'] = user.id
            if Profile.objects.filter(managers = user).exists() and params['request_id'] and params['request_code']:
                profile = Profile.objects.filter(managers = user)[0]
                if Collaboration_request.objects.filter(id = params['request_id'], code = params['request_code'], profile__isnull = True).exists():
                    collaboration = Collaboration_request.objects.get(id = params['request_id'])
                    collaboration.profile = profile
                    collaboration.save()
            if Profile.objects.filter(managers = user).exists() and params['reward_id'] and params['reward_token']:
                profile = Profile.objects.filter(managers = user)[0]
                if Reward_send.objects.filter(id = params['reward_id'], token = params['reward_token']).exists():
                    reward_send = Reward_send.objects.get(id = params['reward_id'])
                    if reward_send.expiration_time < timezone.now():
                        response = {
                            'status':'FAIL',
                            'message':'This gift has already expired.'
                        }
                        return json_response(response)
                    if reward_send.claimed:
                        response = {
                            'status':'FAIL',
                            'message':'This gift has already been claimed.'
                        }
                        return json_response(response)
                    reward_item = Reward_item(reward = reward_send.reward, owner = profile, quantity = reward_send.quantity, expiration_time = reward_send.expiration_time)
                    reward_item.save()
                    reward_send.claimed = True
                    reward_send.save()
                    response = {
                        'status':'REWARD'
                    }
                    return json_response(response)
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
@validate('POST', ['email'])
def create_reset(request, params, user):
    """
    Create a request for password reset
    """
    # Check if session exists
    if user is not None:
        return HttpResponseForbidden('Access forbidden.')
    # Check if account exists
    if not User.objects.filter(email = params['email'], 
                               password__isnull = False).exists():
        response = {
            'status':'FAIL',
            'message':'The email has not been registered yet.'
        }
        return json_response(response)
    user = User.objects.get(email = params['email'])
    expirationTime = timezone.now() + timedelta(days = 3)
    randomCode = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
    resetCode = User_reset_code(user = user, 
                                code = randomCode, 
                                expiration_time = expirationTime)
    resetCode.save()
    sendResetRequestEmail(resetCode)
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('POST', ['password', 'confirm'], ['code'])
def change_password(request, params, user):
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