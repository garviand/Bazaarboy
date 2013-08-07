"""
Controller for files
"""

import uuid
from django.http import HttpResponseBadRequest
from kernel.models import *
from src.controllers.request import validate, json_response
from src.serializer import serialize_one

IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
IMAGE_SIZE_LIMIT = 2621440

@validate('POST')
def upload_image(request, params):
    """
    Upload a image that is stored temporarily
    """
    if not request.FILES.has_key('image_file'):
        return HttpResponseBadRequest('Bad request.')
    rawImage = request.FILES['image_file']
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
    image = Image(source = rawImage)
    image.save()
    response = {
        'status':'OK',
        'image':serialize_one(image)
    }
    return json_response(response)

@validate('POST', ['id'])
def delete_image(request, params):
    """
    Delete a temporarily uploaded image
    """
    if not Image.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'IMAGE_NOT_FOUND',
            'message':'The image doesn\'t exist.'
        }
        return json_response(response)
    image = Image.objects.get(id = params['id'])
    if image.is_archived:
        response = {
            'status':'FAIL',
            'error':'ARCHIVED_IMAGE',
            'message':'The image has been archived.'
        }
        return json_response(response)
    image.delete()
    response = {
        'status':'OK'
    }
    return json_response(response)