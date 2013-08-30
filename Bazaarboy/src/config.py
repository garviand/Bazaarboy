"""
Bazaarboy configurations
"""

import os

BBOY_URL_ROOT = os.getenv('BBOY_URL_ROOT', 'https://www.bazaarboy.com')
BBOY_TRANSACTION_EXPIRATION = 15 # In minutes
BBOY_STATES = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 
    'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 
    'MH', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 
    'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'PW', 'RI', 'SC', 'SD', 'TN', 
    'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY'
]
BBOY_PROFILE_CATEGORIES = [
    'Personal', 'Non-profit', 'Business', 'Other'
]
BBOY_EVENT_CATEGORIES = [
    'Nightlife', 'Charity', 'Other'
]

# WePay

WEPAY_PRODUCTION = False
WEPAY_CLIENT_ID = '105487'
WEPAY_CLIENT_SECRET = 'db3210d4d3'
WEPAY_ACCESS_TOKEN = 'STAGE_91ada7d177ac57e37735802f98422ebc35f08278293d6be9da65449e8f07d074'
WEPAY_APP_FEE_RATIO = 0.04
WEPAY_SCOPE = [
    'manage_accounts', 
    'collect_payments', 
    'view_balance', 
    'view_user', 
    'refund_payments', 
    'preapprove_payments'
]
WEPAY_SUCCESS_STATES = [
    'authorized',
    'reserved',
    'captured',
    'settled'
]

# Mandrill

MANDRILL_API_KEY = 'EJmj_TdbdCy6Xda_9hREKA'
MANDRILL_FROM_EMAIL = 'build@bazaarboy.com'
MANDRILL_FROM_NAME = 'Bazaarboy'