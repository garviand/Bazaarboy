"""
Installation
-- LAMP (sudo apt-get install tasksel, then tasksel)
-- phpmyadmin (sudo apt-get install phpmyadmin) (Include /etc/phpmyadmin/apache.conf in /etc/apache2/apache2.conf)
-- pip (sudo apt-get install python-pip)
-- virtualenvwrapper (sudo pip install virtualenvwrapper)
  -- Edit ~/.bashrc
      Append following lines:
        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/directory-you-do-development-in
        source /usr/local/bin/virtualenvwrapper.sh
      Reactivate bash profile
        source ~/.bashrc
  -- mkvirtualenv bazaarboy
-- python-dev
-- mysql-python
-- django 1.4.5 (pip install Django==1.4.5)
-- django-admin.py startproject Bazaarboy
-- git (sudo apt-get install git)
-- git init
-- Edit .gitignore
  *.pyc *.swp *.log *~ 
-- south (pip install south==0.8.1)
-- fabric (pip install fabric==1.6.1)
"""

from fabric.api import settings, lcd, local

def run():
  with settings(warn_only=True):
    with lcd('./Bazaarboy/'):
      local('python manage.py schemamigration kernel --auto')
      local('python manage.py runserver 0.0.0.0:8080')