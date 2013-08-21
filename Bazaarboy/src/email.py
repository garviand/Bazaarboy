"""
Email utilities
"""

from celery import task
import mandrill


class Email(object):
    """
    A wrapper class for all email functions

    The actual send email request is called asynchronously to reduce blocking.
    """
    def __init__(self):
        super(Email, self).__init__()

    def sendConfirmationEmail(self, confirmationCode, user):
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
         'global_merge_vars': [{'name': 'user_name', 'content':'Eric'}],
         'to': [{'email': 'eric@bazaarboy.com', 'name': 'Andy Garvin'}],
         'track_clicks': True,
         'track_opens': True}

        result = mandrill_client.messages.send_template(template_name='confirm-registration', template_content=template_content, message=message, async=False)

        return result

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