"""
Email utilities
"""

from celery import task

class Email(object):
    """
    A wrapper class for all email functions

    The actual send email request is called asynchronously to reduce blocking.
    """
    def __init__(self):
        super(Email, self).__init__()

    def sendConfirmationEmail(self, confirmationCode):
        pass

    def sendResetRequestEmail(self, resetCode):
        pass

    def sendPasswordChangedEmail(self, user):
        pass

    def sendPurchaseConfirmationEmail(self, purchase):
        pass

    def sendDonationConfirmationEmail(self, donation):
        pass

    def sendWeeklyDigestEmail(self):
        pass