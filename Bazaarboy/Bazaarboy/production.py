# Production Settings

# Use S3 as file storage

AWS_ACCESS_KEY_ID = 'AKIAIX6AKR4TMQL5FSRQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bazaarboy'

DEFAULT_FILE_STORAGE = 'src.s3utils.MediaS3BotoStorage'
STATIC_FILE_STORAGE = 'src.s3utils.StaticS3BotoStorage'

S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL + '/static/'
MEDIA_URL = S3_URL + '/media/'

# Celery

import urllib

BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe = ''), 
                               urllib.quote(AWS_SECRET_ACCESS_KEY, safe = ''))
BROKER_TRANSPORT_OPTIONS = {
    'queue_name_prefix':'bboy-'
}