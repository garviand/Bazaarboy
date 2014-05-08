"""
Controller for all user related actions
"""

import hashlib
import os
import uuid
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone
from facebook import GraphAPI, GraphAPIError
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.email import Email
from src.regex import REGEX_EMAIL
from src.serializer import serialize_one

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
    confirmationCode.user.is_confirmed = True
    confirmationCode.user.save()
    confirmationCode.delete()
    if loggedIn:
        return redirect('index')
    return redirect('user:login')

@login_check()
@validate('GET', [], ['code'])
def reset(request, params, user):
    """
    Reset password page
    """
    if user is not None:
        # Logged user should use their account settings to change password
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
    paymentAccounts = user.payment_account_set.all()
    stripeConnectUrl = r'%s?response_type=code&client_id=%s&scope=%s'
    stripeConnectUrl = stripeConnectUrl % (STRIPE_CONNECT_URL, 
                                           STRIPE_CLIENT_ID, 
                                           STRIPE_SCOPE)
    return render(request, 'user/settings.html', locals())

@login_check()
@validate('POST', ['email', 'password', 'confirm', 'full_name', 'city'])
def create(request, params, user):
    """
    Create a new user using email and password
    """
    # Check if session exists
    if user is not None:
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
    # Check if password and confirm match
    if not params['password'] == params['confirm']:
        response = {
            'status':'FAIL',
            'error':'PASSWORDS_MISMATCH',
            'message':'Password and Confirm Password do not match.'
        }
        return json_response(response)
    # Check if the name is valid
    if len(params['full_name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Your full name is too long.'
        }
        return json_response(response)
    # Check if the city is valid
    if not City.objects.filter(id = params['city']).exists():
        response = {
            'status':'FAIL',
            'error':'CITY_NOT_FOUND',
            'message':'The city doesn\'t exist.'
        }
        return json_response(response)
    city = City.objects.get(id = params['city'])
    # Find the unactivated user, or create a new one
    user = User(email = params['email'])
    if User.objects.filter(email = params['email']).exists():
        user = User.objects.get(email = params['email'])
    # Set the user information
    user.password = params['password']
    user.full_name = params['full_name']
    user.city = city
    user.save()
    # Create the pseudo profile for user
    profile = Profile(name = user.full_name, 
                      description = user.full_name + '\'s personal profile', 
                      community = user.city.pseudo, 
                      category = 'personal')
    profile.save()
    profileManager = Profile_manager(user = user,
                                     profile = profile,
                                     is_creator = True)
    profileManager.save()
    # Creation done, send out a confirmation email
    code = os.urandom(128).encode('base_64')[:128]
    confirmationCode = User_confirmation_code(user = user, code = code)
    confirmationCode.save()
    email = Email()
    email.sendConfirmationEmail(user, confirmationCode)
    email.sendNewAccountEmail(profile)
    # Start the session
    request.session['user'] = user.id
    response = {
        'status':'OK'
    }
    return json_response(response)

@login_check()
@validate('GET', ['email', 'password'])
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
                'message':'You must log in using facebook.'
            }
            return json_response(response)
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
@validate('POST', ['fb_token'], ['email', 'city'])
def fbAuth(request, params, user):
    """
    Authenticate or create a user using a Facebook account
    """
    # Check if session exists
    if user is not None:
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
            if (params['city'] is None or len(params['city']) == 0 or 
                not City.objects.filter(id = params['city']).exists()):
                response = {
                    'status':'FAIL',
                    'error':'INVALID_CITY',
                    'message':'You need to specify a valid city.'
                }
                return json_response(response)
            city = City.objects.get(id = params['city'])
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
            user.full_name = ('%s %s' % (fbProfile['first_name'], 
                                        fbProfile['last_name']))[:50]
            user.city = city
            user.save()
            # Create the pseudo profile for user
            profile = Profile(name = user.full_name, 
                              description = user.full_name + 
                                            '\'s personal profile', 
                              community = user.city.pseudo, 
                              category = 'personal')
            profile.save()
            profileManager = Profile_manager(user = user,
                                             profile = profile,
                                             is_creator = True)
            profileManager.save()
            # Creation done, send out confirmation email
            code = os.urandom(128).encode('base_64')[:128]
            confirmationCode = User_confirmation_code(user = user, code = code)
            confirmationCode.save()
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
def create_reset(request, params, user):
    """
    Create a request for password reset
    """
    # Check if session exists
    if user is not None:
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
                                code = str(uuid.uuid4()), 
                                expiration_time = expirationTime)
    resetCode.save()
    #email = Email()
    #email.sendResetRequestEmail(resetCode)
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
    # Send a notification email to the user
    #email = Email()
    #email.sendPasswordChangedEmail(user)
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