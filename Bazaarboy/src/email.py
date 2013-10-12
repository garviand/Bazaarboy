"""
Email utilities
"""

from datetime import datetime
from celery import task
from mandrill import Mandrill
from django.conf import settings
from kernel.models import *
from src.config import *
from src.timezone import localize

import pdb

class Email(object):
    """
    A wrapper class for all email functions
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
        Email confirming registration
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
        Email containing information to reset password
        """
        to = [{
            'email':user.email, 
            'name':user.full_name
        }]
        subject = 'Reset Your Password'
        template = 'reset-password'
        mergeVars = [
            {
                'name':'user_name', 
                'content':user.full_name
            }, 
            {
                'name': 'reset_code', 
                'content': resetCode.code
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars)

    def sendPasswordChangedEmail(self, user):
        """
        Email regarding the change of password
        """
        to = [{
            'email':user.email, 
            'name':user.full_name
        }]
        subject = 'Your Password Has Been Changed'
        template = 'password-changed'
        mergeVars = [
            {
                'name':'user_name', 
                'content':user.full_name
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars)

    def sendPurchaseConfirmationEmail(self, purchase):
        """
        Send Purchase Confirmation
        """
        coverImageUrl = settings.STATIC_URL + 'images/email-header-event.png'
        if purchase.event.cover is not None:
            coverImageUrl = purchase.event.cover.source.url
        startTime = localize(purchase.event.start_time)
        readableStartTime = startTime.strftime('%b %e, %I:%M %p').lstrip('0')
        creator = Event_organizer.objects.get(event = purchase.event, 
                                              is_creator = True).profile
        contactEmail = creator.managers.all()[0].email
        to = [{
            'email':purchase.owner.email, 
            'name':purchase.owner.full_name
        }]
        subject = 'Confirmation for \'' + purchase.event.name + '\''
        template = 'bboy-p-event-template'
        mergeVars = [
            {
                'name':'event_name', 
                'content':purchase.event.name
            }, 
            {
                'name':'confirmation_code', 
                'content':purchase.code
            },
            {
                'name':'start_time', 
                'content':readableStartTime
            }, 
            {
                'name':'location', 
                'content':purchase.event.location
            },
            {
                'name':'organizer_email', 
                'content':contactEmail
            },
            {
                'name':'cover_image_url', 
                'content':coverImageUrl
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars)

    def sendDonationConfirmationEmail(self, donation):
        """
        Send Donation Confirmation
        """
        to = [{
            'email':donation.owner.email, 
            'name':donation.owner.full_name
        }]
        subject = 'Confirmation for \'' + donation.fundraiser.name + '\''
        template = 'confirm-donation'
        mergeVars = [
            {
                'name':'fundraiser_name', 
                'content':donation.fundraiser.name
            }, 
            {
                'name':'user_name', 
                'content':donation.owner.full_name
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars)