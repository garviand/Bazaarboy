# Production Settings

PREPEND_WWW = True

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
AWS_STORAGE_BUCKET_NAME = 'bazaarboy'

DEFAULT_FILE_STORAGE = 'src.s3utils.MediaS3BotoStorage'
STATICFILES_STORAGE = 'src.s3utils.StaticS3BotoStorage'

S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL + '/static/'
MEDIA_URL = S3_URL + '/media/'

INVITATION_PREFIX = 'prod'