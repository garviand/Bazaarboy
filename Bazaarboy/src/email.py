"""
Email utilities
"""

import cStringIO
import base64
import logging
import qrcode
import urllib
import weasyprint
from datetime import datetime
from celery import task
from mandrill import Mandrill
from django.conf import settings
from django.template import Context
from django.template.loader import *
from kernel.models import *
from src.config import *
from src.timezone import localize

class Email(object):
    """
    A wrapper class for all email functions
    """
    def __init__(self):
        super(Email, self).__init__()
        self.client = Mandrill(MANDRILL_API_KEY)

    def sendEmail(self, to, subject, template, mergeVars, attachments=[]):
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
            'track_opens':True,
            'attachments':attachments
        }
        try:
            result = self.client.messages.send_template(template_name = template, 
                                                        template_content = [], 
                                                        message = message, 
                                                        async = True)
        except Exception, e:
            logging.error(str(e))
            return False
        else:
            return result

    def sendNewAccountEmail(self, profile):
        """
        Email confirming registration
        """
        user = profile.managers.all()[0]
        to = [{
            'email':'eric@bazaarboy.com', 
            'name':'Eric Hamblett'
        }]
        subject = 'A New User Has Been Registered'
        template = 'new-user'
        mergeVars = [
            {
                'name':'user_name', 
                'content':user.full_name
            },
            {
                'name':'email', 
                'content':user.email
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars)

    def sendConfirmationEmail(self, user, confirmationCode):
        """
        Email confirming registration
        """
        to = [{
            'email':user.email, 
            'name':user.full_name
        }]
        subject = 'Welcome to Bazaarboy'
        template = 'welcome-to-bazaarboy'
        mergeVars = [
            {
                'name':'organizer_name', 
                'content':user.full_name
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
        attachments = []
        event = purchase.event
        globalOpts = {
            'event':event.id,
            'title':event.name,
            'start_time':event.start_time,
            'end_time':event.end_time,
            'location':event.location,
            'purchase':purchase.id,
            'tid':purchase.ticket.id,
            'ticket':purchase.ticket.name,
            'seat':'',
        }
        for i in range(0, purchase.quantity):
            opts = globalOpts
            opts['code'] = purchase.code + '-' + str(i + 1)
            ticketAttachment = Ticket_attachment(opts)
            attachments.append({
                'type':'application/pdf',
                'name':opts['code'],
                'content':ticketAttachment.toBase64()
            })
        startTime = localize(purchase.event.start_time)
        readableDate = startTime.strftime('%A, %B %e')
        readableTime = startTime.strftime('%I:%M %p').lstrip('0')
        creator = Event_organizer.objects.get(event = purchase.event, 
                                              is_creator = True).profile
        contactEmail = creator.managers.all()[0].email

        if purchase.ticket.price == 0:
            amount = 0
        else:
            amount = purchase.ticket.price * purchase.quantity
            rate = STRIPE_TRANSACTION_RATE
            amount = int(round((amount * (1 + rate) + 0.5) * 100))
            amount = "{0:.2f}".format(amount/100.0)
        
        to = [{
            'email':purchase.owner.email, 
            'name':purchase.owner.full_name
        }]
        subject = 'Confirmation for \'' + purchase.event.name + '\''
        template = 'event-rsvp'
        mergeVars = [
            {
                'name':'user_name', 
                'content':purchase.owner.full_name
            },
            {
                'name':'event_name', 
                'content':purchase.event.name
            },
            {
                'name':'event_overview', 
                'content':purchase.event.summary
            }, 
            {
                'name':'ticket_name', 
                'content':purchase.ticket.name
            },
            {
                'name':'ticket_quantity', 
                'content':purchase.quantity
            },
            {
                'name':'amount_paid', 
                'content': amount
            },
            {
                'name':'confirmation_code', 
                'content':purchase.code
            },
            {
                'name':'event_id', 
                'content':purchase.event.id
            },
            {
                'name':'event_date', 
                'content':readableDate
            },
            {
                'name':'event_time',
                'content':readableTime
            }, 
            {
                'name':'event_location', 
                'content':purchase.event.location
            },
            {
                'name':'event_map_location', 
                'content':urllib.quote_plus(purchase.event.location)
            },
            {
                'name':'event_address', 
                'content':''
            },
            {
                'name':'organizer_name', 
                'content':creator.name
            },
            {
                'name':'organizer_email', 
                'content':contactEmail
            },
            {
                'name':'event_id', 
                'content':purchase.event.id
            }
        ]
        return self.sendEmail(to, subject, template, mergeVars, attachments)

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

class Attachment(object):
    """
    An abstract attachment object for email
    """
    def getQRCode(self, message):
        """
        Generate qrCode for a message
        """
        qr = qrcode.QRCode(version = 2, box_size = 10, border = 3)
        qr.add_data(message)
        qr.make(fit = True)
        image = qr.make_image()
        buf = cStringIO.StringIO()
        image.save(buf, 'PNG')
        buf.seek(0)
        bufString = buf.read()
        qrString = base64.b64encode(bufString)
        return qrString

    def getPDF(self, params, template):
        """
        Generate PDF from HTML template
        """
        output = template.render(Context(params))
        byteString = weasyprint.HTML(string = output).write_pdf()
        pdfString = base64.b64encode(byteString)
        return pdfString

    def toBase64(self):
        """
        Generate a base64 encoded string for the attachment

        (Abstact, must override)
        """
        return NotImplementedError()

class Ticket_attachment(Attachment):
    """
    A ticket attachment object
    """
    template = get_template('email/ticket.html')

    def __init__(self, opts):
        super(Ticket_attachment, self).__init__()
        self.opts = opts

    def toBase64(self):
        message = 'bboy::%s::%s::%s'
        message = message % (self.opts['event'], self.opts['purchase'], self.opts['tid'])
        self.opts['qrcode'] = self.getQRCode(message)
        output = self.getPDF(self.opts, Ticket_attachment.template)
        return output