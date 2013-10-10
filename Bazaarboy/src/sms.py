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
    def __init__():
        super(SMS, self).__init__()
        self.client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def sendSMS(to, body):
        sms = self.client.sms.messages.create(_from = TWILIO_FROM, to = to, 
                                              body = body)
        return sms

    def sendPurchaseConfirmationSMS(self, purchase):
        body = 'You have RSVP\'d for \''
        body += purchase.event.name
        body += '\' and your confirmation code is '
        body += purchase.code
        return self.sendSMS(purchase.owner.phone)
