"""
Controller for admin
"""

from __future__ import absolute_import
import hashlib
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q, Sum, Count
from django.db.models.loading import get_model
from django.utils import timezone
from datetime import datetime, timedelta
from admin.models import *
from kernel.models import *
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
    # RSVP & Sales Stats
    stats = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        )
    total_stats = stats.aggregate(total_sale = Sum('price'), sale_count = Count('id'))
    monthly_stats = stats.filter(created_time__gte=datetime.now()-timedelta(days=30))
    monthly_stats = monthly_stats.aggregate(total_sale = Sum('price'), sale_count = Count('id'))
    weekly_stats = stats.filter(created_time__gte=datetime.now()-timedelta(days=7))
    weekly_stats = weekly_stats.aggregate(total_sale = Sum('price'), sale_count = Count('id'))
    daily_stats = stats.filter(created_time__gte=datetime.now()-timedelta(days=1))
    daily_stats = daily_stats.aggregate(total_sale = Sum('price'), sale_count = Count('id'))
    # Events (Upcoming/Past)
    upcoming_events = Event.objects.filter(Q(is_launched = True, start_time__gte = timezone.now())).order_by('start_time')[:30]
    past_events = Event.objects.filter(Q(is_launched = True, start_time__lte = timezone.now())).order_by('start_time')[:30]
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

@validate('GET', ['id'])
def login_profile(request, params):
    """
    Admin Login as Profile Manager
    """
    if not request.session.has_key('admin'):
        # No admin session, block from login
        response = {
            'status':'FAIL',
            'message':'Not an Admin.'
        }
        return json_response(response)
    # Find profile manager by profile id and login
    if Profile.objects.filter(id = params['id']).exists():
        profile = Profile.objects.get(id = params['id'])
        manager = profile.managers.all()[0]
        request.session['user'] = manager.id
        response = {
            'status':'OK'
        }
        return json_response(response)
    else:
        response = {
            'status':'FAIL',
            'message':'Profile does not exist.'
        }
        return json_response(response)