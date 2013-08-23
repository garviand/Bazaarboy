"""
Email utilities
"""

from celery import task
from kernel.models import *
import mandrill


class Email(object):
    """
    A wrapper class for all email functions

    The actual send email request is called asynchronously to reduce blocking.
    """
    def __init__(self):
        super(Email, self).__init__()

    def sendConfirmationEmail(self, confirmationCode, resetCode, user):
        """
        Send Confirmation after Registration
        """
        mandrill_client = mandrill.Mandrill('EJmj_TdbdCy6Xda_9hREKA')
        template_content = []
        message = {
         'from_email': 'build@bazaarboy.com',
         'from_name': 'Bazaarboy',
         'headers': {'Reply-To': 'build@bazaarboy.com'},
         'subject': 'Welcome to Bazaarboy',
         'global_merge_vars': [{'name': 'user_name', 'content': user.full_name},{'name': 'confirmation_code', 'content': confirmationCode.code}, {'name': 'reset_code', 'content': resetCode.code}],
         'to': [{'email': user.email, 'name': user.full_name}],
         'track_clicks': True,
         'track_opens': True}

        result = mandrill_client.messages.send_template(template_name='confirm-registration', template_content=template_content, message=message, async=False)

        return result

    def sendResetRequestEmail(self, resetCode, user):
        """
        Send Reset Instructions
        """
        mandrill_client = mandrill.Mandrill('EJmj_TdbdCy6Xda_9hREKA')
        template_content = []
        message = {
         'from_email': 'build@bazaarboy.com',
         'from_name': 'Bazaarboy',
         'headers': {'Reply-To': 'build@bazaarboy.com'},
         'subject': 'Reset Your Password',
         'global_merge_vars': [{'name': 'user_name', 'content': user.full_name}, {'name': 'reset_code', 'content': resetCode.code}],
         'to': [{'email': user.email, 'name': user.full_name}],
         'track_clicks': True,
         'track_opens': True}

        result = mandrill_client.messages.send_template(template_name='reset-password', template_content=template_content, message=message, async=False)

        return result

    def sendPasswordChangedEmail(self, user):
        """
        Send Reset Confirmation
        """
        mandrill_client = mandrill.Mandrill('EJmj_TdbdCy6Xda_9hREKA')
        template_content = []
        message = {
         'from_email': 'build@bazaarboy.com',
         'from_name': 'Bazaarboy',
         'headers': {'Reply-To': 'build@bazaarboy.com'},
         'subject': 'Your Password Has Been Changed',
         'global_merge_vars': [{'name': 'user_name', 'content': user.full_name}],
         'to': [{'email': user.email, 'name': user.full_name}],
         'track_clicks': True,
         'track_opens': True}

        result = mandrill_client.messages.send_template(template_name='password-changed', template_content=template_content, message=message, async=False)

        return result

    def sendPurchaseConfirmationEmail(self, purchase):
        """
        Send Purchase Confirmation
        """
        mandrill_client = mandrill.Mandrill('EJmj_TdbdCy6Xda_9hREKA')
        template_content = []
        message = {
         'from_email': 'build@bazaarboy.com',
         'from_name': 'Bazaarboy',
         'headers': {'Reply-To': 'build@bazaarboy.com'},
         'subject': 'You have RSVP\'d for the event \''+purchase.event.name+'\'',
         'global_merge_vars': [{'name': 'event_name', 'content': purchase.event.name}, {'name': 'confirmation_code', 'content': 'fakecode'}],
         'to': [{'email': purchase.owner.email, 'name': purchase.owner.full_name}],
         'track_clicks': True,
         'track_opens': True}

        result = mandrill_client.messages.send_template(template_name='confirm-rsvp', template_content=template_content, message=message, async=False)

        return result 

    def sendDonationConfirmationEmail(self, donation):
        pass

    def sendWeeklyDigestEmail(self, user):
        pass