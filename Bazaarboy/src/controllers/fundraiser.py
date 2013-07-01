"""
Controller for fundraisers
"""

from django.http import Http404
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one

@login_check()
def index(request, id, loggedIn):
    """
    Fundraiser event page
    """
    if not Fundraiser.objects.filter(id = id).exists():
        return Http404
    fundraiser = Fundraiser.objects.get(id = id)
    return render(request, 'fundraiser.html', locals())

@login_required()
@validate('GET', ['id'])
def fundraiser(request, params):
    pass

@login_required()
@validate('POST', [''], [''])
def create(request, params):
    """
    Create a new fundraiser
    """
    pass

@login_required()
@validate()
def edit(request, params):
    pass

@login_required()
@validate()
def launch(request, params):
    pass

@login_required()
@validate()
def delaunch(request, params):
    pass

@login_required()
@validate()
def delete(request, params):
    pass

@login_required()
@validate()
def donate(request, params):
    pass