#!/bin/bash

if [ ! -d test_venv ]; then
    virtualenv test_venv
fi

source test_venv/bin/activate

pip install -r requirements.txt
pip install -r requirements_test.txt
pip install -r requirements_debug.txt

export NETWORKAPI_PDB=1
export NETWORKAPI_DEBUG=1
export DJANGO_SETTINGS_MODULE='CadVlan.settings'

echo "starting runserver 0.0.0.0:8081"
python manage.py runserver 0.0.0.0:8081
