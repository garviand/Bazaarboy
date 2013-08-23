# Staging Settings

STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')

# Use RDS as database backend

import os

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }

# Use S3 as file storage

AWS_ACCESS_KEY_ID = 'AKIAIX6AKR4TMQL5FSRQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bazaarboy_media_staging'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Celery

import urllib

BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe = ''), 
                               urllib.quote(AWS_SECRET_ACCESS_KEY, safe = ''))
BROKER_TRANSPORT_OPTIONS = {
    'queue_name_prefix':'bboy_staging-'
}