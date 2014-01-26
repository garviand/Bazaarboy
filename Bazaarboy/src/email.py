"""
Email utilities
"""

import cStringIO
import base64
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

def sendEmails(self, to, subject, template, mergeVars, attachments=[]):
    """
    Send an email
    """
    try:
        client = Mandrill(MANDRILL_API_KEY)
        message = {
            'from_email':MANDRILL_FROM_EMAIL,
            'from_name':MANDRILL_FROM_NAME,
            'headers':{
                'Reply-To':MANDRILL_FROM_EMAIL
            },
            'subject':subject,
            'merge_vars':mergeVars,
            'to':to,
            'track_clicks':True,
            'track_opens':True,
            'attachments':attachments
        }
        result = self.client.messages.send_template(template_name = template, 
                                                    template_content = [], 
                                                    message = message, 
                                                    async = True)
    except Exception, e:
        logging.error(str(e))
        return False
    else:
        return result

def sendConfirmationEmail(confirmationCode):
    """
    Email to confirm registration
    """
    user = confirmationCode.user
    to = [{
        'email':user.email, 
        'name':user.full_name
    }]
    subject = 'Welcome to Bazaarboy'
    template = EMAIL_T_ACC_CONFIRMATION
    mergeVars = [{
        rcpt: user.email,
        vars: [
            {
                'name':'user_name', 
                'content':user.full_name
            }, 
            {
                'name':'confirmation_code',
                'content':confirmationCode.code
            }
        ]
    }]
    return Email.sendEmails(to, subject, template, mergeVars)

def sendResetRequestEmail(resetCode):
    """
    Email containing information to reset password
    """
    user = resetCode.user
    to = [{
        'email':user.email, 
        'name':user.full_name
    }]
    subject = 'Reset Your Password'
    template = 'reset-password'
    mergeVars = [{
        rcpt: user.email,
        vars: [
            {
                'name':'user_name', 
                'content':user.full_name
            }, 
            {
                'name': 'reset_code', 
                'content': resetCode.code
            }
        ]
    }]
    return self.sendEmail(to, subject, template, mergeVars)

@task()
def sendEventConfirmationEmail(purchase):
    """
    Send event confirmation
    """
    items = Purchase_item.objects.filter(purchase = purchase) \
                                 .prefetch_related('ticket')
    attachments = Ticket_attachment.getTicketAttachments(purchase, items)
    return

def sendBonusEmails():
    """
    Send emails about the bonus to attendees
    """
    return

def sendRedemptionEmail():
    """
    Send email for the redemption of a bonus
    """
    return

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
        message = message % (self.opts['event'], self.opts['purchase'], 
                             self.opts['item'])
        self.opts['qrcode'] = self.getQRCode(message)
        output = self.getPDF(self.opts, Ticket_attachment.template)
        return output

    @staticmethod
    def getTicketAttachments(self, purchase, items):
        """
        Generate ticket confirmations from purchase items and pack them in 
        the mandrill format dictionary
        """
        attachments = []
        event = purchase.event
        globalOpts = {
            'event':event.id,
            'title':event.name,
            'start_time':event.start_time,
            'end_time':event.end_time,
            'location':event.location,
            'purchase':purchase.id
        }
        i = 1
        for item in items:
            opts = globalOpts
            opts['code'] = '%s-%i' % (purchase.code, i)
            opts['item'] = item.id
            opts['ticket'] = item.ticket.name
            opts['seat'] = ''
            ticketAttachment = Ticket_attachment(opts)
            attachments.append({
                'type':'application/pdf', 
                'name':'Ticket confirmation - %s.pdf' % (opts['code']), 
                'content':ticketAttachment.toBase64()
            })
            i++
        return attachments