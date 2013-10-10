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

# Stripe

STRIPE_CLIENT_ID = os.getenv('STRIPE_CLIENT_ID', 'ca_2Zvu0dHwuN2dHPaiYc1bwqNRbPfvNwMX')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_zjWJjkoeZ06r91JDpSWgK80s')
STRIPE_SCOPE = os.getenv('STRIPE_SCOPE', 'read_write')
STRIPE_OAUTH_ROOT = 'https://connect.stripe.com/oauth/'
STRIPE_CONNECT_URL = STRIPE_OAUTH_ROOT + 'authorize'
STRIPE_TOKEN_URL = STRIPE_OAUTH_ROOT + 'token'
STRIPE_CURRENCY = 'usd'
STRIPE_TRANSACTION_RATE = 0.04
STRIPE_SPONSORSHIP_RATE = 0.01

# Mandrill

MANDRILL_API_KEY = 'EJmj_TdbdCy6Xda_9hREKA'
MANDRILL_FROM_EMAIL = 'build@bazaarboy.com'
MANDRILL_FROM_NAME = 'Bazaarboy'

# Twilio

TWILIO_ACCOUNT_SID = 'ACd8c0aecc8dd23856924ac80483cc8de7'
TWILIO_AUTH_TOKEN = '1d22cb81993f2ab49d2b5ffca8b9bffc'
TWILIO_FROM = '+13148885022'