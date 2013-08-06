"""
Controller for files
"""

import uuid
from django.http import HttpResponseBadRequest
from kernel.models import *
from src.controllers.request import validate

IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
IMAGE_SIZE_LIMIT = 2621440

@validate('POST')
def upload_image(request, params):
    """
    Upload a image that is stored temporarily
    """
    if not request.FILES.has_key('image'):
        return HttpResponseBadRequest('Bad request.')
    rawImage = request.FILES['image']
    imageExt = str(rawImage.name).split('.')[-1].lower()
    if not imageExt in IMAGE_TYPES:
        response = {
            'status':'FAIL',
            'error':'INVALID_FORMAT',
            'message':'The image format is not supported.'
        }
        return json_response(response)
    if rawImage._size > IMAGE_SIZE_LIMIT:
        response = {
            'status':'FAIL',
            'error':'FILE_TOO_BIG',
            'message':'The image cannot be over 2.5MB.'
        }
        return json_response(response)
    imageUid = uuid.uuid4().hex
    rawImage.name = '%s.%s' % (imageUid, imageExt)
    image = Image(original = rawImage)
    image.save()
    