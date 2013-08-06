# Production Settings

# Use S3 as file storage

AWS_ACCESS_KEY_ID = 'AKIAIX6AKR4TMQL5FSRQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bazaarboy_media'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Celery

import urllib

BROKER_URL = 'sqs://%s:%s@' % (urllib.quote(AWS_ACCESS_KEY_ID, safe = ''), 
                               urllib.quote(AWS_SECRET_ACCESS_KEY, safe = ''))