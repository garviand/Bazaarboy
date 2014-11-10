"""
Controller for designs
"""

from __future__ import absolute_import
import hashlib
import uuid
import requests
import stripe
import zipfile
from django.db import transaction
from StringIO import StringIO
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q, Sum, Count
from django.db.models.loading import get_model
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from admin.models import *
from kernel.models import *
from designs.models import *
from src.config import *
from src.controllers.request import *
from src.serializer import serialize_one
from src.regex import REGEX_EMAIL, REGEX_NAME
from src.email import sendEmails

import pdb

@login_check()
@validate('GET', [], ['auth'])
def index(request, params, user):
    """
    Designs index page
    """
    if user:
        if Project.objects.filter(owner = user).exists():
            currentProjects = Project.objects.filter(owner = user, checkout__is_charged = True, is_completed = False).order_by('-id')
            pastProjects = Project.objects.filter(owner = user, checkout__is_charged = True, is_completed = True).order_by('-id')
            return render(request, 'designs/dashboard.html', locals())
        else:
            if params['auth']:
                return redirect('designs:create')
            else:
                return render(request, 'designs/index.html', locals())
    else:
        return render(request, 'designs/index.html', locals())

@login_check()
def review(request, project, user):
    """
    Designs review page
    """
    if not user:
        return redirect('designs:index')
    else:
        if not Project.objects.filter(owner = user, id = project).exists():
            return redirect('designs:index')
        else:
            project = Project.objects.get(id = project)
            newSubmissions = Submission.objects.filter(project = project, is_new = True)
            for submission in newSubmissions:
                submission.is_new = False
                submission.save()
            submissions = []
            services = Service.objects.filter(project = project)
            for service in services:
                if Submission.objects.filter(service = service, project = project).exists():
                    submissions.append(Submission.objects.filter(service = service, project = project).order_by('-id')[0])
            return render(request, 'designs/review.html', locals())

@login_check()
@validate('POST', ['reviews'])
def submit_review(request, user, params):
    """
    Designs review submit
    """
    if not user:
        response = {
            'status':'FAIL',
            'error':'NOT_LOGGED_IN',
            'message': 'You must be logged in.'
        }
        return json_response(response)
    else:
        reviews = json.loads(params['reviews'])
        for subId, comment in reviews.iteritems():
            if not Submission.objects.filter(id = subId, project__owner = user).exists():
                response = {
                    'status':'FAIL',
                    'error':'SUBMISSION_DOES_NOT_EXIST',
                    'message': 'This submission doesn\'t exist.'
                }
                return json_response(response)
            else:
                submission = Submission.objects.get(id = subId)
                project = submission.project
                submission.owner_notes = comment
                submission.save()
        sendReviewEmail(project)
        response = {
            'status':'OK'
        }
        return json_response(response)

@login_check()
def finalize_review(request, user, project):
    """
    Designs finalize
    """
    if not user:
        response = {
            'status':'FAIL',
            'error':'NOT_LOGGED_IN',
            'message': 'You must be logged in.'
        }
        return json_response(response)
    else:
        if not Project.objects.filter(owner = user, id = project).exists():
            response = {
                'status':'FAIL',
                'error':'NOT_OWNER',
                'message': 'This is not your project.'
            }
            return json_response(response)
        project = Project.objects.get(id = project)
        project.is_completed = True
        sendProjectCompleteEmail(project)
        project.save()
        response = {
            'status':'OK',
            'project': project.id
        }
        return json_response(response)

@login_check()
@validate('GET', [], ['code'])
def finalize(request, user, params):
    """
    Finalize Design Project page
    """
    if not params['code']:
        return redirect('designs:index')
    else:
        if Project.objects.filter(code = params['code']).exists():
            project = Project.objects.get(code = params['code'])
            if project.owner:
                if project.owner != user:
                    return redirect('designs:index')
            project_price = 0
            for service in project.services.all():
                project_price += service.price
            return render(request, 'designs/finalize.html', locals())
        else:
            return redirect('designs:index')

@login_check()
def create(request, user):
    """
    Designs create page
    """
    services = Service.objects.all()
    return render(request, 'designs/create.html', locals())

@login_check()
@validate('POST', ['project', 'code'])
def finalize_project(request, params, user):
    if user:
        if Project.objects.filter(code = params['code'], id = params['project']).exists():
            project = Project.objects.get(code = params['code'], id = params['project'])
        else:
            response = {
                'status':'FAIL',
                'error':'PROJECT_DOESNT_EXIST',
                'message': 'This project id or code is incorrect.'
            }
            return json_response(response)
        project.owner = user
        amount = 0
        for service in project.services.all():
            amount += service.price * 100
        paymentAccount = Payment_account.objects.get(id = 44)
        checkout = Checkout(payer = user, 
                            payee = paymentAccount, 
                            amount = amount, 
                            description = 'Bazaarboy Designs')
        checkout.save()
        project.checkout = checkout
        project.save()
        response = {
            'status':'OK',
            'project': serialize_one(project),
            'price':amount,
            'publishable_key':paymentAccount.publishable_key
        }
        return json_response(response)
    else:
        response = {
            'status':'FAIL',
            'error':'NOT_LOGGED_IN',
            'message': 'You must be logged in to finalize your project'
        }
        return json_response(response)

@login_check()
@validate('POST', ['services', 'description'], ['assets'])
def create_project(request, params, user):
    """
    Create Designs Project and, if logged in, a checkout
    """
    paymentAccount = Payment_account.objects.get(id = 43)
    if params['services'] is '':
        response = {
            'status':'FAIL',
            'error':'NO_SERVICE_SELECTED',
            'message':'You must select at least one service'
        }
        return json_response(response)
    designer = Designer.objects.all()[0]
    project = Project(description = params['description'], designer = designer)
    project.save()
    if params['assets'] and params['assets'] is not '':
        assetsRaw = params['assets'].split(",")
        for asset in assetsRaw:
            if Asset.objects.filter(id = asset).exists():
                assetObj = Asset.objects.get(id = asset)
                project.images.add(assetObj)
    servicesRaw = params['services'].split(",")
    amount = 0
    for service in servicesRaw:
        if Service.objects.filter(id = service).exists():
            serviceObj = Service.objects.get(id = service)
            project.services.add(serviceObj)
            amount += serviceObj.price * 100
    if user:
        project.owner = user
        checkout = Checkout(payer = user, 
                            payee = paymentAccount, 
                            amount = amount, 
                            description = 'Bazaarboy Designs')
        checkout.save()
        project.checkout = checkout
        project.save()
        response = {
            'status':'OK',
            'project': serialize_one(project),
            'price':amount,
            'publishable_key':paymentAccount.publishable_key
        }
    else:
        response = {
            'status':'WAIT',
            'project': serialize_one(project)
        }
    return json_response(response)

ASSET_SIZE_LIMIT = 150000000

@csrf_exempt
@validate('POST')
def upload_asset(request, params):
    """
    Upload a asset that is stored temporarily
    """
    if request.FILES.has_key('file'):
        request.FILES['image_file'] = request.FILES['file']
        del request.FILES['file']
    if not request.FILES.has_key('image_file'):
        return HttpResponseBadRequest('Bad request.')
    rawAsset = request.FILES['image_file']
    assetExt = str(rawAsset.name).split('.')[-1].lower()
    if rawAsset._size > ASSET_SIZE_LIMIT:
        response = {
            'status':'FAIL',
            'error':'FILE_TOO_BIG',
            'message':'The file cannot be over 2.5MB.'
        }
        return json_response(response)
    assetUid = uuid.uuid4().hex
    rawAsset.name = '%s' % (assetUid[0:5] + '_' + rawAsset.name)
    asset = Asset(source = rawAsset)
    asset.save()
    response = {
        'status':'OK',
        'image':serialize_one(asset)
    }
    return json_response(response)

@login_check()
@validate('POST', ['checkout', 'stripe_token'])
def charge(request, params, user):
    """
    Charge the checkout to finalize project
    """
    if not Checkout.objects.filter(id = params['checkout']).exists():
        response = {
            'status':'FAIL',
            'error':'CHECKOUT_NOT_FOUND',
            'message':'The checkout doesn\'t exist.'
        }
        return json_response(response)
    checkout = Checkout.objects.get(id = params['checkout'])
    if checkout.is_charged:
        response = {
            'status':'FAIL',
            'error':'ALREADY_CHARGED',
            'message':'The checkout has been charged.'
        }
        return json_response(response)
    try:
        total, fee = STRIPE_TRANSACTION(checkout.amount * 100, False)
        charge = stripe.Charge.create(
            amount = total,
            currency = STRIPE_CURRENCY,
            card = params['stripe_token'],
            description = checkout.description,
            application_fee = 0,
            api_key = checkout.payee.access_token
        )
        checkout.checkout_id = charge.id
        checkout.is_charged = True
        checkout.save()
    except stripe.CardError, e:
        response = {
            'status':'FAIL',
            'error':'CARD_DECLINED',
            'message':'The card is declined.'
        }
        return json_response(response)
    else:
        if Project.objects.filter(checkout = checkout).exists():
            project = Project.objects.get(checkout = checkout)
            sendProjectConfirmationEmail(project)
            sendDesignerConfirmationEmail(project)
        response = {
            'status':'OK'
        }
        return json_response(response)

def sendProjectConfirmationEmail(project):
    """
    Email confirming project
    """
    user = project.owner
    to = [{
        'email':user.email, 
        'name':user.full_name
    }]
    subject = 'Bazaarboy Designs - Project Confirmed'
    template = 'designs-started'
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name':'designer_name', 
                'content':project.designer.first_name
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendSubmissionEmail(submission):
    """
    New Submission Email
    """
    user = submission.project.owner
    to = [{
        'email':user.email, 
        'name':user.full_name
    }]
    subject = 'Bazaarboy Designs - New Submission'
    template = 'designs-submission'
    mergeVars = [{
        'rcpt': user.email,
        'vars': [
            {
                'name':'service_name', 
                'content': submission.service.name
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendDesignerConfirmationEmail(project):
    """
    Email confirming project for designer
    """
    user = project.owner
    to = [{
        'email':project.designer.email, 
        'name':project.designer.first_name + ' ' + project.designer.last_name
    }]
    subject = 'Bazaarboy Designs - New Project'
    template = 'designs-started-designer'
    services = ", ".join(str(service.name) for service in project.services.all())
    mergeVars = [{
        'rcpt': project.designer.email,
        'vars': [
            {
                'name':'designer_name', 
                'content':project.designer.first_name
            },
            {
                'name':'services', 
                'content':services
            },
            {
                'name':'user_email', 
                'content':user.email
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendReviewEmail(project):
    """
    New Review Email
    """
    user = project.owner
    to = [{
        'email':project.designer.email, 
        'name':project.designer.first_name + ' ' + project.designer.last_name
    }]
    subject = 'Bazaarboy Designs - New Review'
    template = 'designs-review'
    mergeVars = [{
        'rcpt': project.designer.email,
        'vars': [
            {
                'name':'user_email', 
                'content':user.email
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

def sendProjectCompleteEmail(project):
    """
    Project Complete Email
    """
    user = project.owner
    to = [{
        'email':project.designer.email, 
        'name':project.designer.first_name + ' ' + project.designer.last_name
    }]
    subject = 'Bazaarboy Designs - Project Complete'
    template = 'designs-complete'
    mergeVars = [{
        'rcpt': project.designer.email,
        'vars': [
            {
                'name':'user_email', 
                'content':user.email
            }
        ]
    }]
    return sendEmails(to, MANDRILL_FROM_NAME, subject, template, mergeVars)

@login_check()
@validate('GET', ['project'])
def download_zip(request, params, user):
    if Project.objects.filter(id = params['project'], owner = user).exists():
        project = Project.objects.get(id = params['project'], owner = user)
    else:
        response = {
            'status':'FAIL',
            'error':'PROJECT_UNAVAILABLE',
            'message':'This project is either not yours or non existent.'
        }
        return json_response(response)
    s = StringIO()
    zf = zipfile.ZipFile(s, "w")
    for asset in project.images.all():
        zf.write(asset.source.url[1:], arcname = 'assets/' + asset.source.name.split("/")[-1])
    zf.close()
    response = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=BazaarboyDesigns.zip'
    return response

@login_check()
@validate('GET', ['project'])
def download_final(request, params, user):
    if Project.objects.filter(id = params['project'], owner = user).exists():
        project = Project.objects.get(id = params['project'], owner = user)
    else:
        response = {
            'status':'FAIL',
            'error':'PROJECT_UNAVAILABLE',
            'message':'This project is either not yours or non existent.'
        }
        return json_response(response)
    s = StringIO()
    zf = zipfile.ZipFile(s, "w")
    services = Service.objects.filter(project = project)
    for service in services:
        if Submission.objects.filter(service = service, project = project).exists():
            submission = Submission.objects.filter(service = service, project = project).order_by('-id')[0]
            for asset in submission.images.all():
                zf.write(asset.source.url[1:], arcname = 'assets/' + asset.source.name.split("/")[-1])
    zf.close()
    response = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=BazaarboyDesigns.zip'
    return response

@designer_check()
def designer(request, designer):
    if not designer:
        return redirect('designs:login_designer')
    else:
        currentProjects = Project.objects.filter(designer = designer, is_completed = False)
        pastProjects = Project.objects.filter(designer = designer, is_completed = True)
        return render(request, 'designs/designer/index.html', locals())

@designer_check()
def designer_project(request, project, designer):
    if not designer:
        return redirect('designs:login_designer')
    else:
        if Project.objects.filter(id = project, designer = designer).exists():
            project = Project.objects.get(id = project, designer = designer)
            submissions = []
            services = Service.objects.filter(project = project)
            for service in services:
                if Submission.objects.filter(service = service, project = project).exists():
                    submissions.append(Submission.objects.filter(service = service, project = project).order_by('-id')[0])
            return render(request, 'designs/designer/project.html', locals())
        else:
            return redirect('designs:designer')

@designer_check()
@validate('POST', ['assets', 'service'], ['notes'])
def designer_submit(request, project, designer, params):
    if not designer:
        response = {
            'status':'FAIL',
            'error':'NOT_LOGGED_IN',
            'message':'Designer not logged in'
        }
        return json_response(response)
    else:
        if Project.objects.filter(id = project, designer = designer).exists():
            project = Project.objects.get(id = project, designer = designer)
            if params['service'] and params['service'] is not '':
                if Service.objects.filter(id = params['service']).exists():
                    service = Service.objects.get(id = params['service'])
            else:
                response = {
                    'status':'FAIL',
                    'error':'NO_SERVICE_SELECTED',
                    'message':'The design service was not selected (Poster, Banner, etc.)'
                }
                return json_response(response)
            notes = ''
            if params['notes']:
                notes = params['notes']
            submission = Submission(project = project, service = service, designer_notes = notes, owner_notes = '')
            submission.save()
            if params['assets'] and params['assets'] is not '':
                assetsRaw = params['assets'].split(",")
                for asset in assetsRaw:
                    if Asset.objects.filter(id = asset).exists():
                        assetObj = Asset.objects.get(id = asset)
                        submission.images.add(assetObj)
            else:
                response = {
                    'status':'FAIL',
                    'error':'NO_ASSETS',
                    'message':'Submission must contain at least 1 asset'
                }
                return json_response(response)
        else:
            response = {
                'status':'FAIL',
                'error':'NOT_CORRECT_DESIGNER',
                'message':'Either this project does not exist or you are not the designer assigned to this project.'
            }
            return json_response(response)
        submission.save()
        sendSubmissionEmail(submission)
        response = {
            'status':'OK'
        }
        return json_response(response)

@designer_check()
def login_designer(request, designer):
    if designer:
        return redirect('designs:designer')
    else:
        return render(request, 'designs/designer/login.html', locals())

@validate('POST', ['email', 'password', 'first_name', 'last_name'])
def create_designer(request, params):
    """
    Create a new designer using email and password
    """
    # Check if admin
    if not request.session.has_key('admin'):
        return HttpResponseForbidden('Access forbidden.')
    # Check if the email has already been registered
    if Designer.objects.filter(email = params['email'], password__isnull = False) \
                   .exists():
        response = {
            'status':'FAIL',
            'error':'DUPLICATE_EMAIL',
            'message':'This email has already been registered.'
        }
        return json_response(response)
    # Check email format
    if not REGEX_EMAIL.match(params['email']):
        response = {
            'status':'FAIL',
            'error':'INVALID_EMAIL',
            'message':'Email format is invalid.'
        }
        return json_response(response)
    # Check password format
    if not 6 <= len(params['password']) <= 16:
        response = {
            'status':'FAIL',
            'error':'INVALID_PASSWORD',
            'message':'The length of password is invalid.'
        }
        return json_response(response)
    # Check if the name is valid
    if (not REGEX_NAME.match(params['first_name']) or 
        not REGEX_NAME.match(params['last_name'])):
        response = {
            'status':'FAIL',
            'error':'INVALID_NAME',
            'message':'Your first or last name contain illegal characters.'
        }
        return json_response(response)
    if len(params['first_name']) > 50 or len(params['last_name']) > 50:
        response = {
            'status':'FAIL',
            'error':'NAME_TOO_LONG',
            'message':'Your first or last name is too long.'
        }
        return json_response(response)
    # Find the unactivated user, or create a new one
    designer = Designer(email = params['email'])
    # Set the user information
    designer.password = params['password']
    designer.first_name = params['first_name']
    designer.last_name = params['last_name']
    designer.save()
    # Start the session
    request.session['designer'] = designer.id
    response = {
        'status':'OK'
    }
    return json_response(response)

@validate('POST', ['email', 'password'])
def auth_designer(request, params):
    """
    Authenticate a designer using email and password
    """
    # Authenticate email and password combination
    if Designer.objects.filter(email = params['email']).exists():
        designer = Designer.objects.get(email = params['email'])
        if designer.password is None:
            response = {
                'status':'FAIL',
                'message':'There is no account associated with this email.'
            }
            return json_response(response)
        saltedPassword = designer.salt + params['password']
        if designer.password == hashlib.sha512(saltedPassword).hexdigest():
            # Email and password match, start session
            request.session['designer'] = designer.id
            response = {
                'status':'OK'
            }
            return json_response(response)
    # Validation failed
    response = {
        'status':'FAIL',
        'message':'Invalid email or password.'
    }
    return json_response(response)