#!/bin/bash

echo -e "\nInstallation for the Bazaarboy environment - Part I\n"
echo -e "Prerequisites:\n"
echo "1. LAMP stack configured with proper credentials (see settings.py)"
echo "2. An empty database in mysql called Bazaarboy"
echo "3. Node.js 0.10.10 environment"
echo -e "3. Do not run this script using sudo\n"

echo "Are these prerequisites satisfied? (If so, type yes):"
read prompt
if [[ $prompt != [Yy][Ee][Ss] ]] ; then
    exit 0
fi

echo -e "\nSome installations require your super user credentials"

# Node packages

command -v node >/dev/null 2>&1 || {
    echo -e "\nNode.js is not installed. Aborting";
    exit 1;
}
echo -e "\nIntalling grunt"
sudo npm install -g grunt-cli
echo -e "\nInstalling node packages\n"
sudo npm install

# Python related

echo -e "\nInstalling gcc/g++ compilers\n" 
sudo apt-get install build-essential
echo -e "\nInstalling python developer package\n"
sudo apt-get install python-dev
echo -e "\nInstalling python-mysqldb\n"
sudo apt-get build-dep python-mysqldb
sudo apt-get install python-mysqldb
echo -e "\nInstalling pip\n"
sudo apt-get install python-pip
echo -e "\nInstalling virtualenvwrapper\n"
sudo pip install virtualenvwrapper
echo -e "\nInstalling PIL requirements\n"
sudo apt-get build-dep python-imaging
sudo ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
sudo ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
sudo ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/

# Others
echo -e "\nInstalling redis\n"
sudo apt-get install redis-server

# Setup virtualenv

echo -e "\nIn another terminal, append the following lines to ~/.bashrc\n\n"
echo "export WORKON_HOME=$HOME/.virtualenvs"
echo "export PROJECT_HOME=$HOME/{{ DEVELOPMENT_DIRECTORY }}"
echo "source /usr/local/bin/virtualenvwrapper.sh"
echo -e "\n\nReplace {{ DEVELOPMENT_DIRECTORY }} with the path of this repo"
echo -e "For example, if this repo is under\n"
echo "~/Development/Bazaarboy"
echo -e "\nThen the line will be\n"
echo -e "export PROJECT_HOME=$HOME/Development/Bazaarboy\n"
echo -e "When you are done, run the following commands:\n"
echo "source ~/.bashrc"
echo "mkvirtualenv bazaarboy"
echo -e "\nThis will setup a virtual environment called bazaarboy"
echo "You should see (bazaarboy) preceeding your bash prompt"
echo "To exit the virtual environment, run 'deactivate'"
echo "And every time you want to do development, run 'workon bazaarboy' first"
echo -e "\nWhen you are in the virtual environment, run setup_virtualenv.bash\n"

exit 0