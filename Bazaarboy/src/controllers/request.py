"""
Some useful methods for handling requests
"""

from functools import wraps
from django.http import *
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
        if param is not None:
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
            if method == 'GET':
                req = req.GET
            elif method == 'POST':
                req = req.POST
            else:
                # Other http methods, do nothing
                return controller(*args, **kwargs)
            params = params_from_request(req, required, optional)
            if not params:
                # Param validation failed, return 400 (Bad Request)
                return HttpResponseBadRequest()
            # Pass the request and stripped params to the controller
            kwargs['request'] = req
            kwargs['params'] = params
            return controller(*args, **kwargs)
        return wraps(controller)(validated_controller)
    return validate_decorator