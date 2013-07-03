import os
from multiprocessing import Process
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
    with lcd('./Bazaarboy/views/'):
        # Jade
        compileJade = lambda: local('jade -w templates/*.jade -o ../templates/')
        processJade = Process(target = compileJade)
        processJade.start()
        # CoffeeScript
        compileCS = lambda: local('coffee -c -w -o ../static/js/ js/')
        processCS = Process(target = compileCS)
        processCS.start()
        # Less
        lessPath = os.path.realpath(os.path.dirname(__file__))
        lessPath += '/Bazaarboy/views/css/'
        with lcd('./css/'):
            for root, dirs, lessFiles in os.walk(lessPath):
                for less in lessFiles:
                    lessName = os.path.splitext(less)[0]
                    local('lessc %s > ../../static/css/%s.css' % (less, 
                                                                  lessName))

def dev(port=8080):
    """
    Start a development environment
    """
    compileProcess = Process(target = compile)
    compileProcess.start()
    with lcd('./Bazaarboy/'):
        with settings(
            hide('warnings'),
            warn_only=True
        ):
            # Check to see if models have changed, if so then migrate
            #local('python manage.py schemamigration kernel --auto')
            pass
        # Run the django development server on specified port
        local('python manage.py runserver 0.0.0.0:%s' % port)