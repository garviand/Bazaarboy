"""
Controller for redeemables
"""

from kernel.models import *
from src.controllers.request import validate, login_required
from src.serializer import serialize_one

@login_required()
@validate('GET', ['id'])
def redeemable(request, params):
    pass

@login_required()
@validate('POST')
def create(request, params):
    pass

@login_required()
@validate('POST')
def edit(request, params):
    pass

@login_required()
@validate('POST')
def delete(request, params):
    pass

@login_required()
@validate('POST')
def redeem(request, params):
    pass