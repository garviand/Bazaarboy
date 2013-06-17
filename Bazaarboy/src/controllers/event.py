"""
Controller for normal events
"""

from django.shortcuts import render
from kernel.models import *
from request import validate, login_required

@login_check()
def index(request, id, loggedIn):
    return render(request, 'event.html', locals())