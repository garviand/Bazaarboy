"""
Some useful methods for handling requests
"""

from functools import wraps
from django.http import *
from django.shortcuts import redirect
import json

def json_response(response):
    """
    A wrapper method to return a http response in JSON format
    """
    return HttpResponse(json.dumps(response))

def params_from_request(req, required=[], optional=[]):
    """
    Strip all the specified parameters from the request object and verify if 
    the required ones are present
    """
    params = {}
    for name in required:
        param = req.get(name, None)
        if param is not None and len(params) > 0:
            params[name] = param
    if len(params.keys()) < len(required):
        return False
    for name in optional:
        param = req.get(name, None)
        params[name] = param
    return params

def validate(method='GET', required=[], optional=[]):
    """
    A decorator to handle the common params checking for controllers. The 
    decorated controller must take in two arguments, request and params
    """
    def validate_decorator(controller):
        def validated_controller(req, *args, **kwargs):
            # Check if the request method matches the specified one
            if req.method != method:
                # Method not allowed, return 405 (Method Not Allowed)
                return HttpResponseNotAllowed([method])
            # Find the correct argument array
            reqArray = None
            if method == 'GET':
                reqArray = req.GET
            elif method == 'POST':
                reqArray = req.POST
            else:
                # Other http methods, do nothing
                return controller(*args, **kwargs)
            params = params_from_request(reqArray, required, optional)
            if not params:
                # Param validation failed, return 400 (Bad Request)
                return HttpResponseBadRequest('Bad request.')
            # Pass the request and stripped params to the controller
            kwargs['request'] = req
            kwargs['params'] = params
            return controller(*args, **kwargs)
        return wraps(controller)(validated_controller)
    return validate_decorator

def login_required(redirectUrl=None, appendNext=True):
    """
    A decorator for controllers that require user to have logged in first
    """
    def login_required_decorator(controller):
        def login_required_controller(req, *args, **kwargs):
            # Check if session exists
            if not req.session.has_key('user'):
                if redirectUrl is not None:
                    return redirect(redirectUrl)
                else:
                    return HttpResponseForbidden('Access forbidden.')
            kwargs['request'] = req
            return controller(*args, **kwargs)
        return wraps(controller)(login_required_controller)
    return login_required_decorator