#!/bin/bash

# Enters Python virtual environment
if [ ! -d venv ]; then
    virtualenv venv
fi
. ./venv/bin/activate


# Resolves the networkapi container IP and sets it on the /etc/hosts
NETAPI_IP=$(nslookup netapi_app | grep Address | tail -1 | awk '{print $2}')
printf "$NETAPI_IP\tnetworkapi.docker\n" >> /etc/hosts

# Installs tests and debugging tools
pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt


# Use NetworkAPI python client library locally
[ ! -d "GloboNetworkAPI-client-python" ] && {
    git clone https://github.com/globocom/GloboNetworkAPI-client-python.git
}

# Update and install as development package
cd GloboNetworkAPI-client-python
git pull origin master
python setup.py develop
cd ..


# Runs WebUI for development purpose
export NETWORKAPI_PDB='1'
export NETWORKAPI_DEBUG=1
export DJANGO_SETTINGS_MODULE='CadVlan.settings'


echo "starting runserver 0.0.0.0:8080"
<<<<<<< HEAD
python manage.py runserver 0.0.0.0:8080
=======
python manage.py runserver 0.0.0.0:8080
>>>>>>> a2b02a7e6b86e10d0c33ddbfb602c23d3e1cfd7e
