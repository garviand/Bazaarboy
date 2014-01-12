"""
Attachment utilities
"""

import cStringIO
import base64
import qrcode
import weasyprint
from django.template import Context
from django.template.loader import *

class Attachment(object):
    """
    A wrapper class for attachment utilities
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

    def getPDF(self, template):
        """
        Generate PDF from HTML String
        """
        byteString = weasyprint.HTML(string = template).write_pdf()
        pdfString = base64.b64encode(byteString)
        return pdfString

    def getTickets(self, event, items):
        """
        Generate ticket confirmations from purchase items
        """
        template = get_template('email/ticket.html')
        pdfs = []
        for item in items:
            message = 'bboy::' + event.id + '::' + item.ticket.id
            message += '::' + item.code
            qr = self.getQRCode(message)
            params = {
                'title':event.name,
                'start_time':event.start_time,
                'end_time':event.end_time,
                'location':event.location,
                'ticket':item.ticket.name,
                'seat':'',
                'code':item.code,
                'qrcode':qr
            }
            output = template.render(Context(params))
            pdf = getPDF(output)
            pdfs.append(pdf)
        return pdfs