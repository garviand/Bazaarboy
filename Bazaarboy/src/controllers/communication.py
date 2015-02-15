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
def email_hook(request, params):
    """
    Webhook For Email Sends Clicks, Opens, etc.
    """
    mandrill_info = json.loads(params['mandrill_events'])
    for info in mandrill_info:
        if 'invite_id' in info['msg']['metadata']:
            if Invite.objects.filter(id = info['msg']['metadata']['invite_id'].split("-", 1)[-1]).exists():
                invite = Invite.objects.get(id = info['msg']['metadata']['invite_id'].split("-", 1)[-1])
                stat, created = Invite_stat.objects.get_or_create(email_id = info['_id'])
                if created:
                    stat.invite = invite
                    stat.event = invite.event
                    stat.profile = invite.profile
                    stat.to = info['msg']['email']
                stat.clicks = len(info['msg']['clicks'])
                stat.opens = len(info['msg']['opens'])
                if 'location' in info:
                    stat.city = info['location']['city']
                    stat.zip_code = info['location']['postal_code']
                stat.save()
                return json_response(serialize_one(stat))
        if 'follow_up_id' in info['msg']['metadata']:
            if Follow_up.objects.filter(id = info['msg']['metadata']['follow_up_id'].split("-", 1)[-1]).exists():
                follow_up = Follow_up.objects.get(id = info['msg']['metadata']['follow_up_id'].split("-", 1)[-1])
                stat, created = Follow_up_stat.objects.get_or_create(email_id = info['_id'])
                if created:
                    stat.follow_up = follow_up
                    stat.event = follow_up.recap.organizer.event
                    stat.profile = follow_up.recap.organizer.profile
                    stat.to = info['msg']['email']
                stat.clicks = len(info['msg']['clicks'])
                stat.opens = len(info['msg']['opens'])
                if 'location' in info:
                    stat.city = info['location']['city']
                    stat.zip_code = info['location']['postal_code']
                stat.save()
                return json_response(serialize_one(stat))
    return json_response({})