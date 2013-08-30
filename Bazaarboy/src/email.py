"""
Email utilities
"""

from celery import task
from mandrill import Mandrill
from kernel.models import *
from src.config import *

class Email(object):
    """
    A wrapper class for all email functions

    The actual send email request is called asynchronously to reduce blocking.
    """
    def __init__(self):
        super(Email, self).__init__()
        self.client = Mandrill(MANDRILL_API_KEY)

    def sendEmail(self, to, subject, template, mergeVars):
        """
        Wrapper function for sending an email
        """
        message = {
            'from_email':MANDRILL_FROM_EMAIL,
            'from_name':MANDRILL_FROM_NAME,
            'headers':{
                'Reply-To': MANDRILL_FROM_EMAIL
            },
            'subject':subject,
            'global_merge_vars':mergeVars,
            'to':to,
            'track_clicks':True,
            'track_opens':True
        }
        result = self.client.messages.send_template(template_name = template, 
                                                    template_content = [], 
                                                    message = message, 
                                                    async = False)
        return result

    def sendConfirmationEmail(self, user, confirmationCode):
        """
        Send Confirmation after Registration
        """
        to = [{
            'email':user.email, 
            'name':user.full_name
        }]
        subject = 'Welcome to Bazaarboy'
        template = 'confirm-registration'
        mergeVars = [
            {
                'name':'user_name', 
                'content':user.full_name
            }, 
            {
                'name':'confirmation_code',
                'content':confirmationCode.code
            }]
        return self.sendEmail(to, subject, template, mergeVars)

    def sendResetRequestEmail(self, resetCode, user):
        """
        Send Reset Instructions
        """
        mandrill_client = Mandrill(MANDRILL_API_KEY)
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
        mandrill_client = Mandrill(MANDRILL_API_KEY)
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
        to = [{
            'email':purchase.owner.email, 
            'name':purchase.owner.full_name
        }]
        subject = 'Confirmation for \'' + purchase.event.name + '\''
        template = 'confirm-rsvp'
        mergeVars = [
            {
                'name':'event_name', 
                'content':purchase.event.name
            }, 
            {
                'name':'confirmation_code', 
                'content':purchase.code
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars)

    def sendDonationConfirmationEmail(self, donation, userProfile):
        """
        Send Donation Confirmation
        """
        mandrill_client = Mandrill(MANDRILL_API_KEY)
        template_content = []
        message = {
         'from_email': 'build@bazaarboy.com',
         'from_name': 'Bazaarboy',
         'headers': {'Reply-To': 'build@bazaarboy.com'},
         'subject': 'Thanks for donating to \''+donation.fundraiser.name+'\'',
         'global_merge_vars': [{'name': 'fundraiser_name', 'content': donation.fundraiser.name}, {'name': 'user_name', 'content': donation.owner.full_name},  {'name': 'user_profile', 'content': userProfile.profile.id}],
         'to': [{'email': donation.owner.email, 'name': donation.owner.full_name}],
         'track_clicks': True,
         'track_opens': True}

        result = mandrill_client.messages.send_template(template_name='confirm-donation', template_content=template_content, message=message, async=False)

        return result

    def sendWeeklyDigestEmail(self, user):
        pass