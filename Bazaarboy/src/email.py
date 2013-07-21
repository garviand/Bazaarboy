"""
Email utilities
"""

from celery import task

class Email:
    """
    A wrapper class for all email functions

    The actual send email request is called asynchronously to reduce blocking.
    """
    def __init__(self):
        super(Email, self).__init__()

    def sendConfirmationEmail(confirmationCode):
        pass

    def sendResetRequestEmail(resetCode):
        pass

    def sendPasswordChangedEmail(user):
        pass

    def sendPurchaseConfirmationEmail(purchase):
        pass

    def sendDonationConfirmationEmail(donation):
        pass

    def sendWeeklyDigestEmail():
        pass