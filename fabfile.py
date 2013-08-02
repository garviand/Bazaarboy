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
    with lcd('./Bazaarboy/'):
        local('python manage.py syncdb')

def test(app=''):
    """
    Run unit tests
    """
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

def dev(port=8080):
    """
    Start a development environment
    """
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