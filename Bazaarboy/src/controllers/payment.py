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
from src.email import sendEventConfirmationEmail, sendRefundConfirmationEmail
from src.sms import sendEventConfirmationSMS
from src.serializer import serialize, serialize_one

import pdb

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
        checkout.checkout_id = charge.id
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

@login_check()
@validate('POST', ['purchase'])
def refund(request, params, user):
    """
    Refund the purchase
    """
    if not Purchase.objects.filter(id = params['purchase']).exists():
        response = {
            'status':'FAIL',
            'error':'PURCHASE_NOT_FOUND',
            'message':'The purchase doesn\'t exist.'
        }
        return json_response(response)
    purchase = Purchase.objects.get(id = params['purchase'])
    if not Organizer.objects.filter(event = purchase.event, 
                                    profile__managers = user).exists():
        response = {
            'status':'FAIL',
            'error':'NOT_A_MANAGER',
            'message':'You don\'t have permission for the event.'
        }
        return json_response(response)
    if not purchase.checkout:
        response = {
            'status':'FAIL',
            'error':'HEADLESS_PURCHASE',
            'message':'This purchase doesn\'t have a checkout.'
        }
        return json_response(response)
    checkout = purchase.checkout
    stripe.api_key = checkout.payee.access_token
    if not checkout.is_charged:
        response = {
            'status':'FAIL',
            'error':'NOT_CHARGED',
            'message':'The checkout has not been charged. There is nothing to refund.'
        }
        return json_response(response)
    if checkout.is_refunded:
        response = {
            'status':'FAIL',
            'error':'ALREADY_REFUNDED',
            'message':'The checkout has already been refunded.'
        }
        return json_response(response)
    if checkout.amount == 0:
        response = {
            'status':'FAIL',
            'error':'FREE_CHECKOUT',
            'message':'The checkout has an amount of 0. There is nothing to refund.'
        }
        return json_response(response)
    try:
        ch = stripe.Charge.retrieve(checkout.checkout_id)
        re = ch.refund()
    except stripe.CardError, e:
        response = {
            'status':'FAIL',
            'error':'REFUND_FAILED',
            'message':'The refund did not go through.'
        }
        return json_response(response)
    else:
        checkout.is_refunded = True
        checkout.save()
        sendRefundConfirmationEmail(purchase, re.amount_refunded)
        response = {
            'status':'OK',
            'purchase': serialize_one(purchase)
        }
        return json_response(response)

@login_check()
@validate('POST', ['invite', 'stripe_token', 'amount'])
def charge_invite(request, params, user):
    """
    Charge for invitation
    """
    if not Invite.objects.filter(id = params['invite']).exists():
        response = {
            'status':'FAIL',
            'error':'INVITE_NOT_FOUND',
            'message':'The invitation doesn\'t exist.'
        }
        return json_response(response)
    invite = Invite.objects.get(id = params['invite'])
    try:
        charge = stripe.Charge.create(
            amount = params['amount'],
            currency = STRIPE_CURRENCY,
            card = params['stripe_token'],
            description = 'Invitations for ' + invite.event.name,
            api_key = STRIPE_SECRET_KEY
        )
    except stripe.CardError, e:
        response = {
            'status':'FAIL',
            'error':'CARD_DECLINED',
            'message':'The card is declined.'
        }
        return json_response(response)
    else:
        invite.paid = True
        invite.price = params['amount']
        invite.save()
        response = {
            'status':'OK',
            'invite': serialize_one(invite)
        }
        return json_response(response)