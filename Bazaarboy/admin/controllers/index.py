"""
Controller for admin
"""

import hashlib
from django.shortcuts import render
from django.http import HttpResponseForbidden
from admin.models import *
from src.controllers.request import json_response, validate

def index(request):
    pass

def login(request):
    """
    Login page for admin
    """
    if request.session.has_key('admin'):
        # Session already exists, redirect to admin index
        return redirect('admin-index')
    return render(request, 'admin/login.html', locals())

@validate('GET', ['name', 'password'])
def auth(request, params):
    """
    Authenticate an admin
    """
    # Check if admin session exists
    if request.session.has_key('admin'):
        return HttpResponseForbidden('Access forbidden.')
    # Authenticate name/password combination
    if Admin.objects.filter(name = params['name']).exists():
        admin = Admin.objects.get(name = params['name'])
        saltedPassword = admin.salt + params['password']
        if admin.password == hashlib.sha512(saltedPassword).hexdigest():
            # Name and password match, start admin session
            sessionAdmin = serialize_one(user, ('id', 'name', 'role'))
            request.session['admin'] = sessionAdmin
            response = {
                'status':'OK'
            }
            return json_response(response)
    # Validate failed
    response = {
        'status':'FAIL',
        'message':'Invalid name and password combination.'
    }
    return json_response(response)
