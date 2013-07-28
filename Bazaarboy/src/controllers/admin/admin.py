"""
Controller for admin
"""

from __future__ import absolute_import
import hashlib
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from admin.models import *
from src.controllers.request import json_response, validate
from src.serializer import serialize_one

def index(request):
    """
    Admin index
    """
    if not request.session.has_key('admin'):
        # No admin session, redirect to login
        return redirect('admin:login')
    admin = request.session['admin']
    return render(request, 'admin/index.html', locals())

def login(request):
    """
    Login page for admin
    """
    if request.session.has_key('admin'):
        # Session already exists, redirect to admin index
        return redirect('admin:index')
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
            sessionAdmin = serialize_one(admin, ('id', 'name', 'role'))
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

def logout(request):
    """
    Logout the admin
    """
    if request.session.has_key('admin'):
        del request.session['admin']
    return redirect('admin:login')