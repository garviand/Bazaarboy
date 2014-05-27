"""
Controller for payments
"""

import json
import requests
import stripe
from django.db import transaction
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.email import sendEventConfirmationEmail
from src.sms import sendEventConfirmationSMS

@login_required('index')
@validate('GET', [], ['code', 'error', 'error_description'])
def connect(request, params, user):
    """
    Connect a payment account to the user's account
    """
    # Check if there is any error
    if params['error'] is not None:
        return redirect('user:settings')
    # Check if a code is passed
    elif params['code'] is not None:
        # Exchange the code for an access token
        tokenParams = {
            'code':params['code'],
            'client_secret':STRIPE_SECRET_KEY,
            'grant_type':'authorization_code'
        }
        response = requests.post(STRIPE_TOKEN_URL, tokenParams)
        response = json.loads(response.content)
        # Check if there is any error
        if response.has_key('error'):
            return HttpResponse(response['error'])
        else:
            # If not, create the payment account
            paymentAccount = Payment_account(
                owner = user,
                user_id = response['stripe_user_id'],
                refresh_token = response['refresh_token'],
                access_token = response['access_token'],
                publishable_key = response['stripe_publishable_key']
            )
            paymentAccount.save()
            profiles = Profile.objects.filter(managers = user)
            profile = profiles[0]
            profile.payment_account = paymentAccount
            profile.save()
            return redirect('user:settings')
    return redirect('user:settings')

@login_check()
@validate('POST', ['checkout', 'stripe_token'])
def charge(request, params, user):
    """
    Charge the checkout
    """
    if not Checkout.objects.filter(id = params['checkout']).exists():
        response = {
            'status':'FAIL',
            'error':'CHECKOUT_NOT_FOUND',
            'message':'The checkout doesn\'t exist.'
        }
        return json_response(response)
    checkout = Checkout.objects.get(id = params['checkout'])
    if not Purchase.objects.filter(checkout = checkout).exists():
        response = {
            'status':'FAIL',
            'error':'HEADLESS_CHECKOUT',
            'message':'This checkout doesn\'t belong to any purchase.'
        }
        return json_response(response)
    purchase = Purchase.objects.get(checkout = checkout)
    creator = Organizer.objects.get(event = purchase.event, 
                                    is_creator = True).profile
    isNonProfit = creator.is_non_profit and creator.is_verified
    tickets = purchase.items.all()
    items = {}
    for ticket in purchase.items.all():
        if ticket.id in items:
            items[ticket.id]['quantity'] += 1
        else:
            items[ticket.id] = {
                'name': ticket.name,
                'quantity': 1
            }
    if checkout.is_charged:
        response = {
            'status':'FAIL',
            'error':'ALREADY_CHARGED',
            'message':'The checkout has been charged.'
        }
        return json_response(response)
    try:
        total, fee = STRIPE_TRANSACTION(checkout.amount * 100, isNonProfit)
        charge = stripe.Charge.create(
            amount = total,
            currency = STRIPE_CURRENCY,
            card = params['stripe_token'],
            description = checkout.description,
            application_fee = fee,
            api_key = checkout.payee.access_token
        )
        checkout.is_charged = True
        checkout.save()
    except stripe.CardError, e:
        response = {
            'status':'FAIL',
            'error':'CARD_DECLINED',
            'message':'The card is declined.'
        }
        return json_response(response)
    else:
        sendEventConfirmationEmail(purchase)
        sendEventConfirmationSMS(purchase)
        response = {
            'status':'OK',
            'tickets': items
        }
        return json_response(response)