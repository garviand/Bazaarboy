"""
Controller for normal events
"""

from django.shortcuts import render
from kernel.models import *
from request import validate, login_required

@login_required()
def index(request, id):
    return render(request, 'event.html', locals())