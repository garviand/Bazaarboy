import multiprocessing
import os
import signal
from fabric.api import *

def console():
    """
    Open up the interactive python console with django context
    """
    with lcd('./Bazaarboy/'):
        local('python manage.py shell')

def docs():
    """
    Generate the project documentation under static/docs/
    """
    with settings(
        hide('warnings'),
        warn_only=True
    ):
        # Delete the old docs if exist
        local('rm -r ./docs/')
    # Use epydoc to generate new docs
    local('epydoc --config docs.config')

def uploads():
    """
    Fix the permission for the uploads folder
    """
    local('sudo chown -R www-data:www-data media/uploads/')

def syncdb():
    """
    Sync the models to database
    """
    # Set up development environment variables
    set_env('development')
    # Sync database
    with lcd('./Bazaarboy/'):
        local('python manage.py syncdb')

def test(app=''):
    """
    Run unit tests
    """
    # Set up development environment variables
    set_env('development')
    # Run tests
    with lcd('./Bazaarboy/'):
        local('python manage.py test %s' % app)

def compile():
    """
    Compile files of sugar into normal format
    """
    with settings(
        hide('warnings'),
        warn_only=True
    ):
        local('grunt dev')

def set_env(env='development'):
    if env == 'development':
        os.environ['BBOY_ENV'] = 'development'
        os.environ['BBOY_DEBUG'] = 'true'
        os.environ['BBOY_MEDIA_URL'] = '/static/media/'
        os.environ['BBOY_STATIC_URL'] = '/static/'
    elif env == 'staging':
        os.environ['BBOY_ENV'] = 'staging'
        os.environ['BBOY_DB_PASS'] = 'bboymafia1'
    elif env == 'production':
        os.environ['BBOY_ENV'] = 'production'

def dev(port=8080):
    """
    Start a development environment
    """
    # Set up development environment variables
    set_env('development')
    # Use worker process to run the watch task
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = multiprocessing.Pool(5, init_worker)
    pool.apply_async(compile)
    try:
        with lcd('./Bazaarboy/'):
            with settings(
                hide('warnings'),
                warn_only=True
            ):
                # Check to see if models have changed, if so then migrate
                #local('python manage.py schemamigration kernel --auto')
                pass
            # Run the celery worker
            #celeryWorker = lambda: local('python manage.py celery worker --loglevel=info')
            #processCelery = Process(target = celeryWorker)
            #processCelery.start()
            # Run the django development server on specified port
            local('python manage.py runserver 0.0.0.0:%s' % port)
    except KeyboardInterrupt:
        pool.close()
        pool.terminate()
        pool.join()
    else:
        pool.close()
        pool.terminate()
        pool.join()