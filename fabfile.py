"""
Installation
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
-- django 1.4.5 (pip install Django==1.4.5)
-- django-admin.py startproject Bazaarboy
-- git (sudo apt-get install git)
-- git init
-- Edit .gitignore
  *.pyc *.swp *.log *~ 
"""