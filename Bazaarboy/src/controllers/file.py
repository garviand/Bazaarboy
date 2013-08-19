"""
Controller for files
"""

import PIL
import uuid
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseBadRequest
from kernel.models import *
from src.controllers.request import validate, json_response
from src.serializer import serialize_one

import pdb

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

@validate('POST', ['id', 'viewport'])
def crop_image(request, params):
    """
    Crop an image by a viewport
    """
    if not Image.objects.filter(id = params['id']).exists():
        response = {
            'status':'FAIL',
            'error':'IMAGE_NOT_FOUND',
            'message':'The image doesn\'t exist.'
        }
        return json_response(response)
    image = Image.objects.get(id = params['id'])
    viewport = params['viewport'].split(',')
    try:
        for i in range(0, 4):
            viewport[i] = int(viewport[i])
            if viewport[i] < 0:
                raise ValueError()
    except (ValueError, IndexError):
        response = {
            'status':'FAIL',
            'error':'INVALID_VIEWPORT',
            'message':'The viewport is invalid.'
        }
        return json_response(response)
    imageUrl = image.source.url
    parts = imageUrl.split('/')
    imageName = parts[-1]
    left = viewport[0]
    upper = viewport[1]
    right = left + viewport[2]
    lower = upper + viewport[3]
    box = left, upper, right, lower
    imageFile = PIL.Image.open(StringIO(image.source.read()))
    croppedImageFile = imageFile.crop(box)
    croppedImageIO = StringIO()
    croppedImageFile.save(croppedImageIO, format = 'JPEG')
    croppedImage = InMemoryUploadedFile(file = croppedImageIO, 
                                        field_name = None, 
                                        name = imageName, 
                                        content_type = 'image/jpeg', 
                                        size = croppedImageIO.len, 
                                        charset = None)
    image.source.delete(save = False)
    image.source = croppedImage
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