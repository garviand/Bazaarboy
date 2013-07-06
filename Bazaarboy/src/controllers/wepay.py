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

@login_required('index')
def checkout(request, id, refType, refId):
    """
    Checkout page
    """
    # Check if checkout is valid
    if not Wepay_checkout.objects.filter(id = id).exists():
        return Http404
    checkout = Wepay_checkout.objects.get(id = id)
    # Check if the user is the payer
    user = User.objects.get(id = request.session['user'])
    if checkout.payer != user:
        return redirect('index')
    # Check if reference is valid
    refModel = Purchase if refType == 'p' else Donation
    if not refModel.objects.filter(id = refId).exists():
        return Http404
    ref = refModel.objects.get(id = refId)
    # Check if the checkout belongs to the reference
    if ref.checkout != checkout:
        return redirect('index')
    # Check if checkout is refunded
    if checkout.is_refunded:
        return redirect('index')
    # Check if checkout is captured
    confirmParams = {
        'id':id,
        'refType':refType,
        'refId':refId
    }
    if checkout.is_captured:
        return redirect('wepay-checkout-confirm', kwargs = confirmParams)
    if checkout.checkout_id is not None:
        wepay = WePay(production = WEPAY_PRODUCTION, 
                      access_token = WEPAY_ACCESS_TOKEN)
        checkoutInfo = wepay.call('/checkout', {
            'checkout_id':checkout.checkout_id
        })
        if checkoutInfo['state'] in WEPAY_SUCCESS_STATES:
            checkout.is_captured = True
            checkout.save()
            return redirect('wepay-checkout-confirm', kwargs = confirmParams)
    checkoutType = 'EVENT' if refType == 'p' else 'DONATION'
    # Create a checkout
    wepay = WePay(production = WEPAY_PRODUCTION, 
                  access_token = checkout.payee.access_token)
    appFee = checkout.amount * WEPAY_APP_FEE_RATIO
    redirectUrl = BBOY_URL_ROOT
    redirectUrl += reverse('wepay-checkout-confirm', kwargs = confirmParams)
    checkoutInfo = wepay.call('/checkout/create', {
        'account_id':checkout.payee.account_id,
        'short_description':checkout.description,
        'type':checkoutType,
        'amount':checkout.amount,
        'app_fee':appFee,
        'redirect_uri':redirectUrl,
        'mode':'iframe'
    })
    checkout.checkout_id = checkoutInfo['checkout_id']
    checkout.save()
    return render(request, 'wepay-checkout.html', locals())

@login_required('index')
def confirm_checkout(request, id, refType, refId):
    """
    Checkout confirmation page
    """
    # Check if checkout is valid
    if not Wepay_checkout.objects.filter(id = id).exists():
        return Http404
    checkout = Wepay_checkout.objects.get(id = id)
    # Check if the user is the payer
    user = User.objects.get(id = request.session['user'])
    if checkout.payer != user:
        return redirect('index')
    # Check if reference is valid
    refModel = Purchase if refType == 'p' else Donation
    if not refModel.objects.filter(id = refId).exists():
        return Http404
    ref = refModel.objects.get(id = refId)
    # Check if the checkout belongs to the reference
    if ref.checkout != checkout:
        return redirect('index')
    # Check if checkout is refunded
    if checkout.is_refunded:
        return redirect('index')
    # Check if checkout is captured
    if not checkout.is_captured:
        if checkout.checkout_id is None:
            return redirect('index')
        else:
            wepay = WePay(production = WEPAY_PRODUCTION, 
                          access_token = WEPAY_ACCESS_TOKEN)
            checkoutInfo = wepay.call('/checkout', {
                'checkout_id':checkout.checkout_id
            })
            if checkoutInfo['state'] in WEPAY_SUCCESS_STATES:
                checkout.is_captured = True
                checkout.save()
            else:
                return redirect('index')
    # Render the confirmation page
    return render(request, 'wepay-checkout-confirm.html', locals())

@login_required('index')
def preapproval(request, id):
    pass

@login_required('index')
def confirm_preapproval(request, id):
    pass