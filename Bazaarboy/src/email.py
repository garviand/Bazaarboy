"""
Email utilities
"""

import cStringIO
import base64
import qrcode
import urllib
import weasyprint
import logging
from datetime import datetime
from celery import task
from mandrill import Mandrill
from django.conf import settings
from django.template import Context
from django.template.loader import *
from kernel.models import *
from src.config import *
from src.timezone import localize
from django.utils.dateformat import DateFormat

import pdb

def sendEmails(to, subject, template, mergeVars, attachments=[]):
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
        result = client.messages.send_template(template_name = template, 
                                                    template_content = [], 
                                                    message = message, 
                                                    async = True)
    except Exception, e:
        logging.error(str(e))
        return False
    else:
        return result

@task
def sendNewAccountEmail(profile):
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
    mergeVars = [{
        'rcpt': 'eric@bazaarboy.com',
        'vars': [
            {
                'name':'profile_name', 
                'content':profile.name
            },
            {
                'name':'user_name', 
                'content':user.first_name + ' ' + user.last_name
            },
            {
                'name':'email', 
                'content':user.email
            }
        ]
    }]
    return sendEmails(to, subject, template, mergeVars)

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
        'rcpt': user.email,
        'vars': [
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
    return sendEmails(to, subject, template, mergeVars)

def sendResetRequestEmail(resetCode):
    """
    Email containing information to reset password
    """
    user = resetCode.user
    to = [{
        'email':user.email, 
        'name':user.user.first_name + ' ' + user.last_name
    }]
    subject = 'Reset Your Password'
    template = 'reset-password'
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name':'user_name', 
                'content':user.first_name + ' ' + user.last_name
            }, 
            {
                'name': 'reset_code', 
                'content': resetCode.code
            }
        ]
    }]
    return self.sendEmail(to, subject, template, mergeVars)

@task()
def sendProfileMessageEmail(name, email, message, profile, event):
    to = [{
        'email':profile.email, 
        'name':name
    }]
    subject = event.name + ' - message from ' + name
    template = 'contact-organizer'
    mergeVars = [{
        'rcpt': profile.email,
        'vars': [
            {
                'name': 'user_name', 
                'content': name
            },
            {
                'name': 'user_email', 
                'content': email
            },
            {
                'name': 'event_name', 
                'content': event.name
            },
            {
                'name': 'user_message', 
                'content': message
            }
        ]
    }]
    return sendEmails(to, subject, template, mergeVars)

@task()
def sendOrganizerAddedEmail(event, adder, profile):
    to = [{
        'email':profile.email, 
        'name':profile.name
    }]
    subject = 'Added as organizer - ' + event.name
    template = 'organizer-added'
    mergeVars = [{
        'rcpt': profile.email,
        'vars': [
            {
                'name': 'adder_name', 
                'content': adder.name
            },
            {
                'name': 'event_id', 
                'content': event.id
            },
            {
                'name': 'event_name', 
                'content': event.name
            }
        ]
    }]
    return sendEmails(to, subject, template, mergeVars)

@task()
def sendEventInvite(event, email, inviter):
    event_month = DateFormat(event.start_time)
    event_month = event_month.format('M')
    event_day = DateFormat(event.start_time)
    event_day = event_day.format('j')
    organizers = event.organizers.all()
    organizer_list_html = ''
    for organizer in organizers:
        if organizer.image:
            organizer_image = """
                <td class='logo' style='-webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: middle; text-align: left; color: #222222; font-family: 'Avenir', 'Helvetica', 'Arial', sans-serif; font-weight: normal; line-height: 19px; font-size: 14px; width: 40px !important; margin: 0; padding: 0px 0px 0;' align='left' valign='middle'>
                    <img src='""" + organizer.image.source.url.split("?", 1)[0] + """' style='outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; width: 35px !important; max-width: 35px !important; float: left; clear: both; display: block;' align='left' />
                </td>
            """
        else:
            organizer_image = ''
        organizer_list_html += """
            <table class='organizer' style='border-collapse: separate; vertical-align: top; text-align: left; margin-bottom: 10px; padding: 0; font-family: 'Avenir', 'Helvetica', 'Arial', sans-serif;'>
                <tr style='vertical-align: top; text-align: left; padding: 0; font-family: 'Avenir', 'Helvetica', 'Arial', sans-serif;' align='left'>
                    """ + organizer_image + """
                    <td class='name' style='-webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: middle; text-align: left; color: #222222; font-family: "Avenir", "Helvetica", "Arial", sans-serif; font-weight: normal; line-height: 19px; font-size: 14px; margin: 0; padding: 0px 0px 0 10px; padding-left: 5px;' align='left' valign='middle'>
                        """ + organizer.name + """
                    </td>
                </tr>
            </table>
        """
    to = [{
        'email':email
    }]
    subject = 'Invitation to \'' + event.name + '\''
    template = 'event-invitation-1'
    mergeVars = [{
        'rcpt': email,
        'vars': [
            {
                'name': 'organizer_list', 
                'content': organizer_list_html
            },
            {
                'name': 'inviter', 
                'content': inviter
            },
            {
                'name': 'event_id', 
                'content': event.id
            },
            {
                'name': 'event_name', 
                'content': event.name
            },
            {
                'name': 'event_month', 
                'content': event_month
            },
            {
                'name': 'event_day', 
                'content': event_day
            },
            {
                'name': 'event_summary', 
                'content': event.summary
            }
        ]
    }]
    return sendEmails(to, subject, template, mergeVars)

@task()
def sendEventConfirmationEmail(purchase):
    """
    Send event confirmation
    """
    user = purchase.owner
    event = purchase.event
    event_month = DateFormat(localize(event.start_time))
    event_month = event_month.format('M')
    event_day = DateFormat(localize(event.start_time))
    event_day = event_day.format('j')
    organizers = event.organizers.all()
    organizer_list_html = ''
    for organizer in organizers:
        if organizer.image:
            organizer_image = """
                <img width="38" class="organizer_logo" src='""" + organizer.image.source.url + """' style="outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; width: auto; max-width: 40px; float: left; clear: both; display: block;" align="left" />
            """
        else:
            organizer_image = ''
        organizer_list_html += """
            <tr class="organizer" style="vertical-align: top; text-align: left; padding: 0;" align="left">
                <td class="three sub-columns center text-pad-left" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: center; min-width: 0px; width: 25%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 10px 10px;" align="center" valign="top">
                    """ + organizer_image + """
                </td>
                <td class="nine sub-columns last" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 75%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 0px 10px;" align="left" valign="top">
                    <div class="organizer_name" style="font-size: 16px; margin-top: 10px;">
                        """ + organizer.name + """
                    </div>
                </td>
                <td class="expander" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; visibility: hidden; width: 0px; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0;" align="left" valign="top">
                </td>
            </tr>
        """
    to = [{
        'email':user.email, 
        'name':user.first_name + ' ' + user.last_name
    }]
    subject = 'Confirmation for \'' + event.name + '\''
    template = 'event-rsvp'
    items = Purchase_item.objects.filter(purchase = purchase) \
                                 .prefetch_related('ticket')
    tickets = {}
    ticket_list_html = ''
    for item in items:
        if item.ticket.id in tickets:
            tickets[item.ticket.id]['quantity'] += 1
        else:
            tickets[item.ticket.id] = {
                'name': item.ticket.name,
                'description': item.ticket.description,
                'price': item.ticket.price,
                'quantity': 1
            }
    for k, ticket in tickets.iteritems():
        if ticket['price'] == 0:
            ticket_price = 'Free'
        else:
            ticket_price = '$'+str(ticket['price'])
        ticket_list_html += """
            <tr class="ticket_top" style="vertical-align: top; text-align: left; padding: 0;" align="left">
                <td class="two sub-columns" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 16.666666%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 10px 10px 0px;" align="left" valign="top">
                    <div class="ticket_count left-text-pad" style="padding-left: 10px; margin-top: 0; font-size: 20px; font-weight: 500; padding-top: 8px;">
                        """ + str(ticket['quantity']) + """x
                    </div>
                </td>
                <td class="two sub-columns" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 16.666666%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 10px 10px 0px;" align="left" valign="top">
                    <div class="ticket_price" style="margin-top: 0; color: #FFF; border-radius: 2px; text-align: center; font-weight: 500; background: #4963E4; padding: 8px 0;" align="center">
                        """ + ticket_price + """
                    </div>
                </td>
                <td class="eight sub-columns last" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 66.666666%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 0px 10px;" align="left" valign="top">
                    <div class="ticket_name right-text-pad" style="padding-right: 10px; margin-top: 0; font-weight: 500; padding-top: 8px;">
                        """ + ticket['name'] + """
                    </div>
                </td>
                <td class="expander" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; visibility: hidden; width: 0px; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0;" align="left" valign="top"></td>
            </tr>
            <tr class="ticket_bottom" style="vertical-align: top; text-align: left; border-bottom-width: thin; border-bottom-color: #F6F6F6; border-bottom-style: solid; padding: 0;" align="left">
                <td class="one sub-columns" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 8.333333%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 10px 10px 0px;" align="left" valign="top">
                </td>
                <td class="one sub-columns" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 8.333333%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 10px 10px 0px;" align="left" valign="top">
                </td>
                <td class="ten sub-columns last" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; min-width: 0px; width: 83.333333%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 0px 10px;" align="left" valign="top">
                    <div class="ticket_description right-text-pad" style="padding-right: 10px; padding-bottom: 10px !important;">
                        """ + ticket['description'] + """
                    </div>
                </td>
                <td class="expander" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: left; visibility: hidden; width: 0px; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0;" align="left" valign="top">
                </td>
            </tr>
        """
    reciept_info = ''
    if purchase.amount > 0:
        reciept_info = 'TOTAL: $' + str(purchase.amount)
    if event.slug:
        event_url = 'https://bazaarboy.com/' + event.slug
    else:
        event_url = 'https://bazaarboy.com/event/' + str(event.id)
    startTime = localize(event.start_time)
    if event.end_time:
        endTime = localize(event.end_time)
        if endTime.day == startTime.day:
            event_date = '<span style="font-weight: 600;">' + startTime.strftime('%A') + '</span>, '
            event_date += startTime.strftime('%I:%M%p').lower() + ' - ' + endTime.strftime('%I:%M%p').lower()
        else:
            event_date = startTime.strftime('%A') + ', ' + startTime.strftime('%I:%M%p').lower() + ' - '
            event_date += endTime.strftime('%A') + ', ' + endTime.strftime('%I:%M%p').lower()
    else:
        event_date = '<span style="font-weight: 600;">' + startTime.strftime('%A') + '</span>, '
        event_date += startTime.strftime('%I:%M%p').lower()
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name': 'organizer_list', 
                'content': organizer_list_html
            },
            {
                'name': 'ticket_list', 
                'content': ticket_list_html
            },
            {
                'name': 'event_link', 
                'content': event_url
            },
            {
                'name': 'primary_organizer', 
                'content': organizers[0].name
            },
            {
                'name': 'event_name', 
                'content': event.name
            },
            {
                'name': 'event_month', 
                'content': event_month
            },
            {
                'name': 'event_day', 
                'content': event_day
            },
            {
                'name': 'event_date', 
                'content': event_date
            },
            {
                'name': 'event_location', 
                'content': event.location
            },
            {
                'name': 'reciept_info', 
                'content': reciept_info
            }
        ]
    }]
    attachments = Ticket_attachment.getTicketAttachments(purchase, items)
    return sendEmails(to, subject, template, mergeVars, attachments)

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
    def getTicketAttachments(purchase, items):
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
            i += 1
        return attachments