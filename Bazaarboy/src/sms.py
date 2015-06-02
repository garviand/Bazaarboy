"""
SMS utilities
"""

import logging
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from src.config import *

import pdb

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

def sendMMS(to, message, image):
    """
    Send an MMS
    """
    try:
        client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        mms = client.messages.create(to=to, from_=TWILIO_FROM, body=message, media_url=[image])
    except Exception, e:
        logging.error(str(e))
        return False
    else:
        return mms

def sendEventConfirmationSMS(purchase):
    """
    Send out event confirmation SMS
    """
    body = 'You have RSVP\'d for \''
    body += purchase.event.name
    body += '\' and your confirmation code is '
    body += purchase.code
    body += '. Thanks!'
    for item in purchase.items.all():
        if item.attachment:
            name, extension = os.path.splitext(item.attachment.name)
            if extension.lower() in ['.gif', '.jpg', '.jpeg', '.png']:
                return sendMMS(purchase.owner.phone, body, item.attachment.url.split("?", 1)[0])
        else:
            return sendSMS(purchase.owner.phone, body)
    return True

def sendClaimMMS(claim):
    """
    Send out claim MMS
    """
    if len(claim.owner.phone) == 10:
        if claim.item.claim_instructions:
            message = claim.item.claim_instructions
        else:
            message = 'To redeem \'' + claim.item.reward.name + '\', present this link to \'' + claim.item.reward.creator.name + '\''
        message += '\n\nRedeem: https://bazaarboy.com/r/?id=' + str(claim.id) + '&code=' + claim.code 
        return sendMMS(claim.owner.phone, message, claim.item.reward.attachment.source.url.split("?", 1)[0])
    return True
