"""
Controller for communication
"""

import cgi
import json
import simplejson
import os
import re
import ordereddict
from datetime import timedelta
from django.db import transaction, IntegrityError
from django.db.models import F, Q, Count, Sum
from django.http import Http404
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.views.decorators.cache import cache_page
from django.core.serializers.json import DjangoJSONEncoder
from celery import task
from kernel.models import *
from kernel.templatetags import layout
from src.config import *
from src.controllers.request import *
from src.serializer import serialize, serialize_one
from src.sms import sendEventConfirmationSMS
from mandrill import Mandrill
from django.views.decorators.csrf import csrf_exempt

import pdb
import operator

@csrf_exempt
@validate('POST', [], ['mandrill_events'])
def invite_hook(request, params):
    """
    Webhook For Invitation Clicks, Opens, etc.
    """
    mandrill_info = json.loads(params['mandrill_events'])
    for info in mandrill_info:
        stat, created = Invite_stat.objects.get_or_create(email_id = info['_id'])
        stat.to = info['msg']['email']
        stat.clicks = len(info['msg']['clicks'])
        stat.opens = len(info['msg']['opens'])
        stat.city = info['location']['city']
        stat.zip_code = info['location']['postal_code']
        stat.save()
    return json_response(serialize_one(stat))