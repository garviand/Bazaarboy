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
from src.controllers.request import validate, login_required

@login_required('index')
def authorize(request):
    """
    Redirect user to authorize the creation of a WePay account
    """
    wepay = WePay(production = WEPAY_PRODUCTION, 
                  access_token = WEPAY_ACCESS_TOKEN)
    redirectUrl = BBOY_URL_ROOT + reverse('wepay-create')
    scope = ','.join(WEPAY_SCOPE)
    authorizationUrl = wepay.get_authorization_url(redirect_uri = redirectUrl, 
                                                   client_id = WEPAY_CLIENT_ID, 
                                                   scope = scope)
    return redirect(authorizationUrl)

@login_required('index')
@validate('GET', ['code'], ['name'])
def create(request, params):
    """
    Create a WePay account for the user
    """
    if params['name'] is None:
        # User has authorized, prompt for a legal name
        return render(request, 'wepay-create.html', locals())
    # Legal name acquired, request for an access token
    wepay = WePay(production = WEPAY_PRODUCTION, 
                  access_token = WEPAY_ACCESS_TOKEN)
    redirectUrl = BBOY_URL_ROOT + reverse('wepay-create')
    tokenInfo = wepay.get_token(redirect_uri = redirectUrl, 
                                client_id = WEPAY_CLIENT_ID, 
                                client_secret = WEPAY_CLIENT_SECRET, 
                                code = params['code'])
    # Access token acquired, create the account
    accountRequest = {
        'name':params['name'],
        'description':'Account for Bazaarboy platform.'
    }
    accountInfo = wepay.call('/account/create', accountRequest)
    user = User.objects.get(id = request.session['user'])
    wepayAccount = Wepay_account(owner = user, 
                                 user_id = tokenInfo['user_id'], 
                                 account_id = accountInfo['account_id'], 
                                 access_token = tokenInfo['access_token'], 
                                 name = params['name'])
    wepayAccount.save()
    return redirect('index')

def create_checkout(obj):
    """
    Create a checkout on WePay based on a purchase or donation
    """
    checkout = obj.checkout
    appFee = checkout.amount * WEPAY_APP_FEE_RATIO
    checkoutParams = {
        'account_id':checkout.payee.account_id,
        'short_description':checkout.description,
        'amount':checkout.amount,
        'app_fee':appFee,
        'mode':'iframe'
    }
    if type(obj) == Purchase:
        checkoutParams['type'] = 'EVENT'
    else:
        checkoutParams['type'] = 'DONATION'
    checkoutInfo = wepay.call('/checkout/create', checkoutParams)
    checkout.checkout_id = checkoutInfo['checkout_id']
    checkout.save()
    return checkout