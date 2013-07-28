#!/bin/bash

echo -e "\nInstallation for Bazaarboy environment - Part II\n"
echo -e "\nDo not run this script using sudo\n"

echo "Are you in the virtual environment? (If so, type yes):"
read prompt
if [[ $prompt != [Yy][Ee][Ss] ]] ; then
    exit 0
fi

# Other python packages

echo -e "\nInstalling dependent python packages\n"
pip install -r pip.list

echo -e "\nDevelopment environment is now finished!"
echo -e "Run 'fab dev' to kickstart your development process!\n"

exit 0