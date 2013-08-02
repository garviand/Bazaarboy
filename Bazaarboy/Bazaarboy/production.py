# Production Settings

# Use S3 as file storage

AWS_ACCESS_KEY_ID = 'AKIAJVHJSPLDIV7XVLUQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bazaarboy_media'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Celery

import urllib

BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe = ''), 
                               urllib.quote(AWS_SECRET_ACCESS_KEY, safe = ''))