#!/bin/bash
sudo killall gunicorn
sudo /usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py cadvlan_wsgi:application
tail -f CadVlan/log.log
