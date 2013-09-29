"""
Controller for payments
"""

import json
import requests
import stripe
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from kernel.models import *
from src.config import *
from src.controllers.request import *
from src.email import Email

import pdb

@login_required('index')
@validate('GET', [], ['code', 'error', 'error_description'])
def connect(request, params, user):
    """
    Connect a payment account to the user's account
    """
    # Check if there is any error
    if params['error'] is not None:
        pass
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
            pass
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
    if user is not None and checkout.payer != user:
        response = {
            'status':'FAIL',
            'error':'PERMISSION_DENIED',
            'message':'You don\'t have permission for the checkout.'
        }
        return json_response(response)
    if checkout.is_charged:
        response = {
            'status':'FAIL',
            'error':'ALREADY_CHARGED',
            'message':'The checkout has been charged.'
        }
        return json_response(response)
    try:
        fee = int(checkout.amount * STRIPE_TRANSACTION_RATE)
        charge = stripe.Charge.create(
            amount = checkout.amount,
            currency = STRIPE_CURRENCY,
            card = params['stripe_token'],
            description = checkout.description,
            application_fee = fee,
            api_key = checkout.payee.access_token
        )
        checkout.is_charged = True
        checkout.save()
        response = {
            'status':'OK'
        }
        return json_response(response)
    except stripe.CardError, e:
        response = {
            'status':'FAIL',
            'error':'CARD_DECLINED',
            'message':'The card is declined.'
        }
        return json_response(response)
