"""
Controller for WePay
"""

from __future__ import absolute_import
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from kernel.models import *
from wepay import WePay
from src.config import *
from src.controllers.request import *
from src.email import Email

import pdb

@login_required('index')
def authorize(request, user):
    """
    Redirect user to authorize the creation of a WePay account
    """
    wepay = WePay(production = WEPAY_PRODUCTION, 
                  access_token = WEPAY_ACCESS_TOKEN)
    redirectUrl = BBOY_URL_ROOT + reverse('wepay:create')
    scope = ','.join(WEPAY_SCOPE)
    authorizationUrl = wepay.get_authorization_url(redirect_uri = redirectUrl, 
                                                   client_id = WEPAY_CLIENT_ID, 
                                                   scope = scope)
    return redirect(authorizationUrl)

@login_required('index')
@validate('GET', ['code'])
def create(request, params, user):
    """
    Create a WePay account for the user
    """
    # Use code to request for an access token
    wepay = WePay(production = WEPAY_PRODUCTION, 
                  access_token = WEPAY_ACCESS_TOKEN)
    redirectUrl = BBOY_URL_ROOT + reverse('wepay:create')
    tokenInfo = wepay.get_token(redirect_uri = redirectUrl, 
                                client_id = WEPAY_CLIENT_ID, 
                                client_secret = WEPAY_CLIENT_SECRET, 
                                code = params['code'])
    # Access token acquired, create the account
    accountRequest = {
        'name':user.full_name,
        'description':'Account for Bazaarboy platform.'
    }
    accountInfo = wepay.call('/account/create', accountRequest)
    wepayAccount = Wepay_account(owner = user, 
                                 user_id = tokenInfo['user_id'], 
                                 account_id = accountInfo['account_id'], 
                                 access_token = tokenInfo['access_token'], 
                                 name = user.full_name)
    wepayAccount.save()
    return redirect('index')

@validate('POST', [], 
          ['account_id', 'checkout_id', 'type', 'account'])
def ipn(request, params):
    """
    Endpoint for WePay IPN
    """
    if params['account_id'] is not None:
        # Account status change
        pass
    elif params['checkout_id'] is not None:
        if params['type'] is not None and params['account'] is not None:
            if params['type'].lower() == 'purchase':
                try:
                    # Try get all related objects out of database
                    account = Wepay_account.objects.get(id = params['account'])
                    wepay = WePay(production = WEPAY_PRODUCTION, 
                                  access_token = account.access_token)
                    checkoutParams = {
                        'checkout_id':params['checkout_id']
                    }
                    checkoutInfo = wepay.call('/checkout/', checkoutParams)
                    checkout = Wepay_checkout.objects \
                                             .get(checkout_id = params['checkout_id'])
                    purchase = Purchase.objects.get(checkout = checkout)
                except Exception:
                    pass
                else:
                    # See if the checkout is successful
                    if checkoutInfo['state'] in WEPAY_SUCCESS_STATES:
                        # If so, mark it
                        checkout.is_captured = True
                        checkout.save()
                        # Send confirmation email
                        email = Email()
                        email.sendPurchaseConfirmationEmail(purchase)
            elif params['type'].lower() == 'donation':
                pass
            elif params['type'].lower() == 'sponsorship':
                pass
    return json_response({})

def create_checkout(_type, account, description, amount, extra):
    """
    Create a checkout on WePay
    """
    wepay = WePay(production = WEPAY_PRODUCTION, 
                  access_token = account.access_token)
    appFee = amount * WEPAY_APP_FEE_RATIO
    callbackUri = BBOY_URL_ROOT + reverse('wepay:ipn') + '?' + extra
    checkoutParams = {
        'type':_type.upper(),
        'account_id':account.account_id,
        'short_description':description,
        'amount':amount,
        'app_fee':appFee,
        'callback_uri':callbackUri,
        'mode':'iframe'
    }
    checkout = wepay.call('/checkout/create', checkoutParams)
    return checkout