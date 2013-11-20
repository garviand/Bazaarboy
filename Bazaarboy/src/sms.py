"""
SMS utilities
"""

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from src.config import *

class SMS(object):
    """
    A wrapper class for all the SMS functions
    """
    def __init__(self):
        super(SMS, self).__init__()
        self.client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def sendSMS(self, to, body):
        sms = self.client.sms.messages.create(_from = TWILIO_FROM, to = to, 
                                              body = body)
        return sms

    def sendPurchaseConfirmationSMS(self, purchase):
        if len(purchase.owner.phone) == 10:
            body = 'You have RSVP\'d for \''
            body += purchase.event.name
            body += '\' and your confirmation code is '
            body += purchase.code
            #body += '. From Bazaarboy.'
            return self.sendSMS(purchase.owner.phone, body)
        return True
