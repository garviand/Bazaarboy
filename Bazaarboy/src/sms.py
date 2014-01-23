"""
SMS utilities
"""

import logging
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from src.config import *

def sendSMS(to, body):
    """
    Send an SMS
    """
    try:
        client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        sms = client.sms.messages.create(_from = TWILIO_FROM, to = to, body = body)
    except Exception, e:
        logging.error(str(e))
        return False
    else:
        return sms

def sendEventConfirmationSMS(purchase):
    """
    Send out event confirmation SMS
    """
    if len(purchase.owner.phone) == 10:
        body = 'You have RSVP\'d for \''
        body += purchase.event.name
        body += '\' and your confirmation code is '
        body += purchase.code
        body += '. Thanks!'
        return sendSMS(purchase.owner.phone, body)
    return True
