"""
Controller for files
"""

import PIL.Image
import uuid
import requests
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from kernel.models import *
from src.controllers.request import validate, json_response
from src.serializer import serialize_one

import pdb

IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
IMAGE_CONTENT_TYPES = {
    'jpg':'image/jpeg',
    'jpeg':'image/jpeg',
    'png':'image/png',
    'gif':'image/gif'
}
IMAGE_SIZE_LIMIT = 2621440

@csrf_exempt
@validate('POST')
def upload_csv(request, params):
    """
    Upload a image that is stored temporarily
    """
    if not request.FILES.has_key('file'):
        return HttpResponseBadRequest('Bad request.')
    rawCsv = request.FILES['file']
    csvExt = str(rawImage.name).split('.')[-1].lower()
    if not csvExt == 'csv':
        response = {
            'status':'FAIL',
            'error':'INVALID_FORMAT',
            'message':'The image format is not supported.'
        }
        return json_response(response)
    if rawCsv._size > IMAGE_SIZE_LIMIT:
        response = {
            'status':'FAIL',
            'error':'FILE_TOO_BIG',
            'message':'The csv cannot be over 2.5MB.'
        }
        return json_response(response)
    csvUid = uuid.uuid4().hex
    rawCsv.name = '%s.%s' % (csvUid, csvExt)
    csv = Csv(source = rawImage)
    csv.save()
    response = {
        'status':'OK',
        'file':serialize_one(csv)
    return json_response(response)

@csrf_exempt
@validate('POST')
def upload_image(request, params):
    """
    Upload a image that is stored temporarily
    """
    isFromRedactor = False
    if request.FILES.has_key('file'):
        request.FILES['image_file'] = request.FILES['file']
        del request.FILES['file']
        isFromRedactor = True
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
    if isFromRedactor:
        redactorImage = image.source.url.split("?", 1)
        response = {
            'filelink':redactorImage[0]
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
    imageName = imageUrl.split('/')[-1].split('?')[0]
    imageExt = imageName.split('.')[-1].lower()
    imageFormat = 'jpeg' if imageExt == 'jpg' else imageExt
    imageContentType = IMAGE_CONTENT_TYPES[imageExt]
    left = viewport[0]
    upper = viewport[1]
    right = left + viewport[2]
    lower = upper + viewport[3]
    box = left, upper, right, lower
    imageFile = PIL.Image.open(StringIO(image.source.read()))
    croppedImageFile = imageFile.crop(box)
    croppedImageIO = StringIO()
    croppedImageFile.save(croppedImageIO, format = imageFormat)
    croppedImage = InMemoryUploadedFile(file = croppedImageIO, 
                                        field_name = None, 
                                        name = imageName, 
                                        content_type = imageContentType, 
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

@csrf_exempt
@validate('POST', ['url', 'event'])
def aviary(request, params):
    """
    Aviary handler
    """
    if not Event.objects.filter(id = params['event']).exists():
        response = {
            'status':'FAIL',
            'error':'EVENT_NOT_FOUND',
            'message':'The event does not exist.'
        }
        return json_response(response)
    imageRequest = requests.get(params['url'])
    imageUid = uuid.uuid4().hex
    imageExt = params['url'].split('.')[-1]
    imageName = '%s.%s' % (imageUid, imageExt)
    imageIO = StringIO(imageRequest.content)
    aviaryImage = InMemoryUploadedFile(file = imageIO,
                                       field_name = None, 
                                       name = imageName, 
                                       content_type = IMAGE_CONTENT_TYPES[imageExt],
                                       size = imageIO.len, 
                                       charset = None)
    image = Image(source = aviaryImage, is_archived = True)
    image.save()
    event = Event.objects.get(id = params['event'])
    event.cover = image
    event.save()
    response = {
        'status':'OK'
    }
    return json_response(response)