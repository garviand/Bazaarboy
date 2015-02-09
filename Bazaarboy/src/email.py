"""
Email utilities
"""

import cStringIO
import base64
import mimetypes
import qrcode
import urllib
import urllib2
import weasyprint
import logging
import hashlib
import uuid
import pytz
from datetime import datetime, timedelta
from celery import task
from mandrill import Mandrill
from django.conf import settings
from django.template import Context
from django.template.loader import *
from kernel.models import *
from src.config import *
from src.timezone import localize
from django.utils import timezone
from django.utils.dateformat import DateFormat
from pygeocoder import Geocoder
from kernel.templatetags import layout

import pdb

def sendEmails(to, from_name, subject, template, mergeVars, attachments=[]):
    """
    Send an email
    """
    try:
        client = Mandrill(MANDRILL_API_KEY)
        message = {
            'from_email':MANDRILL_FROM_EMAIL,
            'from_name':from_name,
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

@task()
def sendEventInvite(invite, recipients):
    to = []
    mergeVars = []
    for recipient in recipients:
        to.append({'email':recipient})
        mergeVars.append({
            'rcpt': recipient,
            'vars': [
                {
                    'name': 'unsub_key',
                    'content': hashlib.sha512(recipient + UNSUBSCRIBE_SALT).hexdigest()
                },
                {
                    'name': 'user_email',
                    'content': recipient
                }
            ]
        })
    buttonHtml = '<a href="https://bazaarboy.com/' + layout.eventUrl(invite.event) + '" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: #FFFFFF; border: thin solid ' + invite.color + ';">RSVP</a>'
    if invite.image:
        headerImageHtml = '<img align="left" alt="" src="' + invite.image.source.url.split("?", 1)[0] + '" width="564" style="max-width: 757px;padding-bottom: 0;display: inline !important;vertical-align: bottom;border: 0;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;" class="mcnImage">'
    else:
        headerImageHtml = ''
    if invite.profile.image:
        organizerLogo = "<img src='" + invite.profile.image.source.url.split("?", 1)[0] + "' style='max-width: 100px; max-height: 100px; padding-bottom: 0;display: inline !important;vertical-align: bottom;border: 0;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;' align='center' />"
    else:
        organizerLogo = ''
    inviteDetails = ''
    if invite.details:
        inviteDetails = invite.details
    globalVars = [
        {
            'name':'profile_name', 
            'content': invite.profile.name
        },
        {
            'name':'profile_id', 
            'content': invite.profile.id
        },
        {
            'name':'header_image', 
            'content': headerImageHtml
        },
        {
            'name':'event_date_short', 
            'content': layout.standardTime(invite.event.start_time)
        },
        {
            'name':'event_name', 
            'content': invite.event.name
        },
        {
            'name':'event_date', 
            'content': layout.standardDate(invite.event)
        },
        {
            'name':'message', 
            'content': invite.message
        },
        {
            'name':'rsvp_button', 
            'content': buttonHtml
        },
        {
            'name':'details', 
            'content': inviteDetails
        },
        {
            'name':'organizer_logo', 
            'content': organizerLogo
        },
        {
            'name':'event_link', 
            'content': 'https://bazaarboy.com/' + layout.eventUrl(invite.event)
        }
    ]
    template = 'new-invite'
    subject = 'Invitation to \'' + invite.event.name + '\''
    attachments = []
    try:
        client = Mandrill(MANDRILL_API_KEY)
        message = {
            'from_email':MANDRILL_FROM_EMAIL,
            'from_name':invite.profile.name,
            'headers':{
                'Reply-To':MANDRILL_FROM_EMAIL
            },
            'subject':subject,
            'merge_vars':mergeVars,
            'global_merge_vars':globalVars,
            'to':to,
            'track_clicks':True,
            'track_opens':True,
            'attachments':attachments,
            'metadata':{
                'invite_id':settings.INVITATION_PREFIX + '-' + str(invite.id),
                'invite_event_id':settings.INVITATION_PREFIX + '-' + str(invite.event.id),
                'profile_id':settings.INVITATION_PREFIX + '-' + str(invite.profile.id)
            }
        }
        result = client.messages.send_template(template_name = template, 
                                                    template_content = [], 
                                                    message = message, 
                                                    async = True)
    except Exception, e:
        logging.error(str(e))
        return False
    else:
        if Invite.objects.filter(id = invite.id).exists():
            invite = Invite.objects.get(id = invite.id)
            invite.recipients = len(recipients)
            invite.is_sent = True
            invite.sent_at = timezone.now()
            invite.save()
            return result

@task()
def sendFollowUp(follow_up, recipients):
    to = []
    mergeVars = []
    for recipient in recipients:
        to.append({'email':recipient})
        mergeVars.append({
            'rcpt': recipient,
            'vars': [
                {
                    'name': 'unsub_key',
                    'content': hashlib.sha512(recipient + UNSUBSCRIBE_SALT).hexdigest()
                },
                {
                    'name': 'user_email',
                    'content': recipient
                }
            ]
        })
    buttonHtml = '<a href="' + follow_up.button_target + '" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: transparent; border: thin solid ' + follow_up.color + ';">' + follow_up.button_text + '</a>'
    if follow_up.image:
        headerImageHtml = '<img align="left" alt="" src="' + follow_up.image.source.url.split("?", 1)[0] + '" style="max-width: 600px !important; height: auto; line-height: 100%; outline: none; text-decoration: none; display: block; border: 0;" class="mcnImage">'
    else:
        headerImageHtml = ''
    if follow_up.recap.organizer.profile.image:
        organizerLogo = "<img src='" + follow_up.recap.organizer.profile.image.source.url.split("?", 1)[0] + "' style='max-width: 150px; height: auto; max-height: 150px; line-height: 100%; outline: none; text-decoration: none; display: block; border: 0;' />"
    else:
        organizerLogo = ''
    globalVars = [
        {
            'name':'profile_name', 
            'content': follow_up.recap.organizer.profile.name
        },
        {
            'name':'profile_id', 
            'content': follow_up.recap.organizer.profile.id
        },
        {
            'name':'header_image', 
            'content': headerImageHtml
        },
        {
            'name':'event_name', 
            'content': follow_up.recap.organizer.event.name
        },
        {
            'name':'message', 
            'content': follow_up.message
        },
        {
            'name':'button_html', 
            'content': buttonHtml
        },
        {
            'name':'heading', 
            'content': follow_up.heading
        },
        {
            'name':'organizer_logo', 
            'content': organizerLogo
        },
        {
            'name':'color', 
            'content': follow_up.color
        }
    ]
    template = 'follow-up'
    subject = '\'' + follow_up.recap.organizer.event.name + '\' - Thanks for coming!'
    attachments = []
    if follow_up.attachment:
        name, extension = os.path.splitext(follow_up.attachment.source.file.name)
        content = urllib2.urlopen(follow_up.attachment.source.url).read().encode('base64')
        attachments.append({
            'type': mimetypes.guess_type(follow_up.attachment.source.file.name)[0], 
            'name': name+extension,
            'content': content
        })
    try:
        client = Mandrill(MANDRILL_API_KEY)
        message = {
            'from_email':MANDRILL_FROM_EMAIL,
            'from_name':follow_up.recap.organizer.profile.name,
            'headers':{
                'Reply-To':MANDRILL_FROM_EMAIL
            },
            'subject':subject,
            'merge_vars':mergeVars,
            'global_merge_vars':globalVars,
            'to':to,
            'track_clicks':True,
            'track_opens':True,
            'attachments':attachments,
            'metadata':{
                'follow_up_id':settings.INVITATION_PREFIX + '-' + str(follow_up.id),
                'follow_up_event_id':settings.INVITATION_PREFIX + '-' + str(follow_up.recap.organizer.event.id),
                'profile_id':settings.INVITATION_PREFIX + '-' + str(follow_up.recap.organizer.profile.id)
            }
        }
        result = client.messages.send_template(template_name = template, 
                                                    template_content = [], 
                                                    message = message, 
                                                    async = True)
    except Exception, e:
        logging.error(str(e))
        return False
    else:
        if Follow_up.objects.filter(id = follow_up.id).exists():
            follow_up = Follow_up.objects.get(id = follow_up.id)
            follow_up.recipients = len(recipients)
            follow_up.is_sent = True
            follow_up.sent_at = timezone.now()
            follow_up.save()
            return result

@task()
def sendRecapReminder(organizer):
    to = [{
        'email': organizer.profile.email, 
        'name': organizer.profile.name
    }]
    subject = '\'' + organizer.event.name + '\' has ended - Manage Attendees'
    template = 'recap-reminder'
    buttonHtml = '<a href="https://bazaarboy.com" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: #FFFFFF; border: thin solid ' + organizer.event.color + ';">My Dashboard</a>'
    if organizer.profile.image:
        organizerLogo = "<img src='" + organizer.profile.image.source.url.split("?", 1)[0] + "' style='max-width: 100px; max-height: 100px; padding-bottom: 0;display: inline !important;vertical-align: bottom;border: 0;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;' align='center' />"
    else:
        organizerLogo = ''
    if organizer.is_creator:
        recapText = 'It\'s time to add the attendees to a list and send out your follow up communitcation!'
    else:
        recapText = 'It\'s time to add the attendees to a list!'
    mergeVars = [{
        'rcpt': organizer.profile.email,
        'vars': [
            {
                'name':'profile_name', 
                'content': organizer.profile.name
            },
            {
                'name':'profile_id', 
                'content': organizer.profile.id
            },
            {
                'name':'event_date_short', 
                'content': layout.standardTime(organizer.event.start_time)
            },
            {
                'name':'event_name', 
                'content': organizer.event.name
            },
            {
                'name':'event_date', 
                'content': layout.standardDate(organizer.event)
            },
            {
                'name':'action_button', 
                'content': buttonHtml
            },
            {
                'name':'organizer_logo', 
                'content': organizerLogo
            },
            {
                'name':'recap_text',
                'content': recapText
            }
        ]
    }]

    if organizer.event.end_time is not None:
        mark_time = organizer.event.end_time
    else:
        mark_time = organizer.event.start_time
    local_time = localize(mark_time)
    if local_time.hour < 5:
        send_time_local = local_time + timedelta(hours = (12-local_time.hour))
    else:
        send_time_local = local_time + timedelta(hours = (36-local_time.hour))
    df = DateFormat(send_time_local.astimezone(pytz.utc))
    send_time = df.format('Y-m-d H:i:s')
    attachments = []

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
                                                    async = True,
                                                    send_at = send_time)
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
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

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
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendResetRequestEmail(resetCode):
    """
    Email containing information to reset password
    """
    user = resetCode.user
    to = [{
        'email':user.email,
        'name':user.first_name + ' ' + user.last_name
    }]
    subject = 'Reset Your Password'
    template = 'reset-password'
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name':'user_name', 
                'content':user.first_name
            }, 
            {
                'name': 'reset_code', 
                'content': resetCode.code
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendCollaborationRequest(collaboration):
    """
    Email prompting event collaboration
    """
    subject = 'Invitation to Collaborate - ' + collaboration.event.name
    template = 'collaboration-request'
    organizer = collaboration.sender
    if organizer.profile.image:
        organizerLogo = "<img src='" + organizer.profile.image.source.url.split("?", 1)[0] + "' style='max-width: 100px; max-height: 100px; padding-bottom: 0;display: inline !important;vertical-align: bottom;border: 0;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;' align='center' />"
    else:
        organizerLogo = ''
    # Profile Invited Directly
    if collaboration.profile is not None:
        profile = collaboration.profile
        to = [{
            'email':profile.email,
            'name':profile.name
        }]
        reciever = profile.email
        buttonHtml = '<a href="https://bazaarboy.com/" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: #FFFFFF; border: thin solid ' + collaboration.event.color + ';">My Dashboard</a>'
        action_text = 'Check your dashboard to accept or reject the request.'
    else:
        to = [{
            'email':collaboration.email
        }]
        reciever = collaboration.email
        buttonHtml = '<a href="https://bazaarboy.com/login?requestid=' + str(collaboration.id) + '&requestc=' + collaboration.code + '" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: #FFFFFF; border: thin solid ' + collaboration.event.color + ';">Log In</a>'
        buttonHtml += '<br><br>or<br><br>'
        buttonHtml += '<a href="https://bazaarboy.com/register?requestid=' + str(collaboration.id) + '&requestc=' + collaboration.code + '" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: #FFFFFF; border: thin solid ' + collaboration.event.color + ';">Register</a>'
        action_text = 'Log In or Create an Account to respond to the collaboration request.'
    mergeVars = [{
        'rcpt': reciever,
        'vars': [
            {
                'name':'organizer_logo', 
                'content':organizerLogo
            }, 
            {
                'name': 'organizer_name', 
                'content': organizer.profile.name
            },
            {
                'name': 'event_name', 
                'content': organizer.event.name
            },
            {
                'name': 'action_text', 
                'content': action_text
            },
            {
                'name': 'action_button', 
                'content': buttonHtml
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendCollaborationResponse(collaboration, accepted):
    """
    Email prompting event collaboration
    """
    subject = 'Collaboration Response - ' + collaboration.event.name
    template = 'collaboration-response'
    organizer = collaboration.sender
    if collaboration.profile.image:
        organizerLogo = "<img src='" + collaboration.profile.image.source.url.split("?", 1)[0] + "' style='max-width: 100px; max-height: 100px; padding-bottom: 0;display: inline !important;vertical-align: bottom;border: 0;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;' align='center' />"
    else:
        organizerLogo = ''
    to = [{
        'email':organizer.profile.email,
        'name':organizer.profile.name
    }]
    buttonHtml = '<a href="https://bazaarboy.com/" class="primary-btn view_event_btn" style="color: #222222; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; font-size: 1.2em; box-sizing: border-box; padding: 12px 60px;background: #FFFFFF; border: thin solid ' + collaboration.event.color + ';">My Dashboard</a>'
    if accepted:
        organizer_action = '\'' + collaboration.profile.name + '\' has accepted your collaboration request for the event:'
        action_text = 'Congratulations on working together!'
    else:
        organizer_action = '\'' + collaboration.profile.name + '\' has rejected your collaboration request for the event:'
        action_text = 'You may want to contact the collaborator directly.'
    mergeVars = [{
        'rcpt': organizer.profile.email,
        'vars': [
            {
                'name':'organizer_logo', 
                'content':organizerLogo
            }, 
            {
                'name': 'organizer_action', 
                'content': organizer_action
            },
            {
                'name': 'event_name', 
                'content': organizer.event.name
            },
            {
                'name': 'action_text', 
                'content': action_text
            },
            {
                'name': 'action_button', 
                'content': buttonHtml
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendRefundConfirmationEmail(purchase, amount):
    """
    Email refund reciept
    """
    refund_amount = '$' + '{0:.02f}'.format(float(amount) / 100.0)
    user = purchase.owner
    if purchase.event.slug:
        event_url = 'https://bazaarboy.com/' + purchase.event.slug
    else:
        event_url = 'https://bazaarboy.com/event/' + str(purchase.event.id)
    subject = 'You Have Been Refunded - Bazaarboy'
    template = 'refund'
    to = [{
        'email':user.email, 
        'name':user.first_name + ' ' + user.last_name
    }]
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name':'user_name', 
                'content':user.first_name
            }, 
            {
                'name':'event_name', 
                'content':purchase.event.name
            },
            {
                'name':'refund_amount', 
                'content':refund_amount
            },
            {
                'name':'event_link', 
                'content':event_url
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

@task()
def sendIssueEmail(name, email, message, event):
    if event.slug:
        event_url = 'https://bazaarboy.com/' + event.slug
    else:
        event_url = 'https://bazaarboy.com/event/' + str(event.id)
    to = [{
        'email': 'eric@bazaarboy.com', 
        'name': 'Bazaarboy'
    }]
    subject = event.name + ' - RSVP issue from ' + name
    template = 'issue'
    mergeVars = [{
        'rcpt': 'eric@bazaarboy.com',
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
                'name': 'event_url', 
                'content': event_url
            },
            {
                'name': 'user_message', 
                'content': message
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

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
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

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
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

@task()
def sendManualEventInvite(event, email, subject, inviter, custom_message=''):
    if Unsubscribe.objects.filter(email = email).exists():
        return False
    event_month = DateFormat(localize(event.start_time))
    event_month = event_month.format('M')
    event_day = DateFormat(localize(event.start_time))
    event_day = event_day.format('j')
    organizers = event.organizers.all()
    organizer_list_html = ''
    if event.slug:
        event_url = 'https://bazaarboy.com/' + event.slug
    else:
        event_url = 'https://bazaarboy.com/event/' + str(event.id)
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
    if custom_message.strip() != '':
        custom_message = "<i>" + custom_message + "</i>"
    to = [{
        'email':email
    }]
    if subject.strip() == '':
        subject = 'Invitation to \'' + event.name + '\''
    key = hashlib.sha512(email + UNSUBSCRIBE_SALT).hexdigest()
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
                'name': 'custom_message', 
                'content': custom_message
            },
            {
                'name': 'event_link', 
                'content': event_url
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
            },
            {
                'name': 'user_email', 
                'content': email
            },
            {
                'name': 'unsub_key', 
                'content': key
            }
        ]
    }]
    return sendEmails(to, inviter, subject, template, mergeVars)

def sendEventReminder(purchase, tz):
    """
    Send event reminder 24 hours before event
    """
    user = purchase.owner
    event = purchase.event
    event_month = DateFormat(localize(event.start_time))
    event_month = event_month.format('M')
    event_day = DateFormat(localize(event.start_time))
    event_day = event_day.format('j')
    organizers = event.organizers.all()
    to = [{
        'email':user.email, 
        'name':user.first_name + ' ' + user.last_name
    }] 
    subject = 'Reminder for ' + event.name
    from_name = organizers[0].name
    from_email = ''
    if organizers[0].email:
        from_email = organizers[0].email
    template = 'event-reminder'
    items = Purchase_item.objects.filter(purchase = purchase) \
                                 .prefetch_related('ticket')
    reciept_info = ''
    if event.slug:
        event_url = 'https://bazaarboy.com/' + event.slug
    else:
        event_url = 'https://bazaarboy.com/event/' + str(event.id)
    startTime = event.start_time.astimezone(tz)
    startTime = tz.normalize(startTime)
    if event.end_time:
        endTime = event.end_time.astimezone(tz)
        endTime = tz.normalize(endTime)
        if endTime.day == startTime.day:
            event_date = '<span style="font-weight: 600;">' + startTime.strftime('%A') + '</span>, '
            event_date += startTime.strftime('%I:%M%p').lower() + ' - ' + endTime.strftime('%I:%M%p').lower()
        else:
            event_date = startTime.strftime('%A') + ', ' + startTime.strftime('%I:%M%p').lower() + ' - '
            event_date += endTime.strftime('%A') + ', ' + endTime.strftime('%I:%M%p').lower()
    else:
        event_date = '<span style="font-weight: 600;">' + startTime.strftime('%A') + '</span>, '
        event_date += startTime.strftime('%I:%M%p').lower()
    event_address = ''
    event_map = ''
    if event.latitude and event.longitude:
        event_address += "<div style='margin-bottom:5px; text-decoration:underline;'>Event Address</div>"
        address = Geocoder.reverse_geocode(event.latitude, event.longitude)
        address = [x.strip() for x in address[0].formatted_address.split(',')]
        for address_component in address:
            if address_component != 'USA':
                event_address += str(address_component) + "<br />"
        event_map = u'<a href="https://maps.google.com/?saddr=' + str(event.latitude) + ',' + str(event.longitude) + '"><img src="http://maps.google.com/maps/api/staticmap?center=' + str(event.latitude) + ',' + str(event.longitude) + '&zoom=15&size=300x150&markers=' + str(event.latitude) + ',' + str(event.longitude) + '" /></a>'
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name': 'first_name', 
                'content': user.first_name
            },
            {
                'name': 'organizer_email', 
                'content': from_email
            },
            {
                'name': 'event_link', 
                'content': event_url
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
                'name': 'event_address', 
                'content': event_address
            },
            {
                'name': 'event_map', 
                'content': event_map
            }
        ]
    }]
    attachments = Ticket_attachment.getTicketAttachments(purchase, items)
    return sendEmails(to, from_name, subject, template, mergeVars, attachments)

@task()
def sendEventConfirmationEmail(purchase, manual=False, inviter=None):
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
                <img width="38" class="organizer_logo" src='""" + organizer.image.source.url + """' style="outline: none; text-decoration: none; width:40px; max-width: 40px; float: left; display: block;" align="left" />
            """
        else:
            organizer_image = ''
        organizer_list_html += """
            <tr class="organizer" style="vertical-align: top; text-align: left; padding: 0;" align="left">
                <td width="40" class="three sub-columns center text-pad-left" style="word-break: break-word; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto; border-collapse: collapse !important; vertical-align: top; text-align: center; min-width: 0px; width: 25%; line-height: 19px; font-size: 14px; color: #4A4A4A !important; margin: 0; padding: 0px 10px 10px;" align="center" valign="top">
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
    if manual:
        subject = 'You\'re on the Guest List - \'' + event.name + '\'' 
        header_text = 'You have been added to the guest list by <b>' + inviter.profile.name + '</b>'
        from_name = inviter.profile.name
    else:  
        subject = 'Confirmation for \'' + event.name + '\''
        header_text = 'CONFIRMATION | Your tickets to <b>' + organizers[0].name + '\'s</b> Event'
        from_name = organizers[0].name
    template = 'confirm-rsvp'
    items = Purchase_item.objects.filter(purchase = purchase) \
                                 .prefetch_related('ticket')
    attFiles = []
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
            if item.ticket.attachment:
                attFiles.append(item.ticket.attachment.url)
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
    if purchase.amount > 0 and not manual:
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
                'name': 'header_text', 
                'content': header_text
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
    for f in attFiles:
        parts = f.split('/')
        name, filetype, tail = parts[-1].partition('.pdf')
        if settings.BBOY_ENV == 'development':
            content = open(f.lstrip('/')).read().encode('base64')
        else:
            content = urllib2.urlopen(f).read().encode('base64')
        attachments.append({
            'type': mimetypes.guess_type(f)[0], 
            'name': name+filetype,
            'content': content
        })
    return sendEmails(to, from_name, subject, template, mergeVars, attachments)

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
            'purchase':purchase.id,
            'name':purchase.owner.first_name + ' ' + purchase.owner.last_name
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