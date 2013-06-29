"""
Bazaarboy configurations
"""

BBOY_URL_ROOT = 'http://localhost:8080'

# WePay

WEPAY_PRODUCTION = False
WEPAY_CLIENT_ID = '105487'
WEPAY_CLIENT_SECRET = 'db3210d4d3'
WEPAY_ACCESS_TOKEN = 'STAGE_a1195e1ef347334b39b9bfb449b676c75250444a3a2e7c60aa63aceffd5c2126'
WEPAY_APP_FEE_RATIO = 0.04
WEPAY_SCOPE = [
    'manage_accounts', 
    'collect_payments', 
    'view_balance', 
    'view_user', 
    'refund_payments', 
    'preapprove_payments'
]