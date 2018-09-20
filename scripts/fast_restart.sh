#!/bin/bash

echo "exporting NETWORKAPI_DEBUG=1"
export NETWORKAPI_DEBUG=1

echo "killing gunicorn"
sudo killall gunicorn

echo "starting gunicorn"
sudo /usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py wsgi:application

tail -f CadVlan/log.log
