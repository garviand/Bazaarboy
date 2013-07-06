"""
Some useful methods for handling requests
"""

import json
from functools import wraps
from django.http import *
from django.shortcuts import redirect
from django.utils import timezone

FORMAT_DATETIME = '%Y-%m-%d %X'

def json_response(response):
    """
    A wrapper method to return a http response in JSON format
    """
    response['timestamp'] = float(timezone.now().strftime('%s'))
    return HttpResponse(json.dumps(response))

def params_from_request(requestArray, required=[], optional=[], 
                        parseIfFlagged=True):
    """
    Strip all the specified parameters from the request object and verify if 
    the required ones are present
    """
    # A shortcut function to parse the param by its flag
    def parseByFlag(name, param):
        if param is not None:
            if name[:3] == 'is_':
                param = param == '1'
            elif name[-5:] == '_time':
                from datetime import datetime
                param = datetime.strptime(param, FORMAT_DATETIME) \
                                .replace(tzinfo = timezone.utc)
        return param
    # Strip the params
    params = {}
    for name in required:
        param = requestArray.get(name, None)
        if param is not None and len(param) > 0:
            if parseIfFlagged:
                param = parseByFlag(name, param)
            params[name] = param
    if len(params.keys()) < len(required):
        return False
    for name in optional:
        param = requestArray.get(name, None)
        if parseIfFlagged:
            param = parseByFlag(name, param)
        params[name] = param
    return params

def validate(method='GET', required=[], optional=[]):
    """
    A decorator to handle the common params checking for controllers. The 
    decorated controller must take in two arguments, request and params
    """
    def validate_decorator(controller):
        def validated_controller(request=None, *args, **kwargs):
            if request is None:
                request = kwargs['request']
            # Check if the request method matches the specified one
            if request.method != method:
                # Method not allowed, return 405 (Method Not Allowed)
                return HttpResponseNotAllowed([method])
            # Find the correct argument array
            requestArray = None
            if method == 'GET':
                requestArray = request.GET
            elif method == 'POST':
                requestArray = request.POST
            else:
                # Other http methods, do nothing
                return controller(request, *args, **kwargs)
            params = params_from_request(requestArray, required, optional)
            if params is False:
                # Param validation failed, return 400 (Bad Request)
                return HttpResponseBadRequest('Bad request.')
            # Pass the stripped params to the controller
            kwargs['params'] = params
            return controller(request, *args, **kwargs)
        return wraps(controller)(validated_controller)
    return validate_decorator

def login_required(redirectUrl=None):
    """
    A decorator to force login
    """
    def login_required_decorator(controller):
        def login_required_controller(request=None, *args, **kwargs):
            if request is None:
                request = kwargs['request']
            # Check if session exists
            if not request.session.has_key('user'):
                if redirectUrl is not None:
                    return redirect(redirectUrl)
                else:
                    return HttpResponseForbidden('Access forbidden.')
            return controller(request, *args, **kwargs)
        return wraps(controller)(login_required_controller)
    return login_required_decorator

def login_check():
    """
    A decorator to check the login status
    """
    def login_check_decorator(controller):
        def login_checked_controller(request=None, *args, **kwargs):
            if request is None:
                request = kwargs['request']
            # Check if session exists
            kwargs['loggedIn'] = request.session.has_key('user')
            return controller(request, *args, **kwargs)
        return wraps(controller)(login_checked_controller)
    return login_check_decorator

def admin_required(roleRequirement=None):
    """
    A decorator to force admin login
    """
    def admin_required_decorator(controller):
        def admin_required_controller(request=None, *args, **kwargs):
            if request is None:
                request = kwargs['request']
            # Check if admin session exists
            if not request.session.has_key('admin'):
                return HttpResponseForbidden('Access forbidden.')
            # Check if the admin level reaches requirement
            if (roleRequirement == 'Super' and 
                request.session['admin']['role'] != 'S'):
                return HttpResponseForbidden('Permission denied.')
            return controller(request, *args, **kwargs)
        return wraps(controller)(admin_required_controller)
    return admin_required_decorator