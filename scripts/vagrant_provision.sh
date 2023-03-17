apt-get update
apt-get install gcc -y
apt-get install libldap2-dev libsasl2-dev libssl-dev -y
apt-get install python-ldap -y
apt-get install memcached -y
apt-get install python-pip -y
apt-get install python-dev -y
apt-get install git -y
pip install -r /vagrant/requirements.txt
pip install gunicorn

echo -e "PYTHONPATH=\"/vagrant/:$PYTHONPATH\"" >> /etc/environment
echo -e '#!/bin/bash\n/usr/local/bin/gunicorn -c /vagrant/gunicorn.conf.py wsgi:application' > /etc/init.d/gunicorn_cadvlan
chmod 777 /etc/init.d/gunicorn_cadvlan
update-rc.d gunicorn_cadvlan defaults
export PYTHONPATH="/vagrant:$PYTHONPATH"
/usr/local/bin/gunicorn  -c /vagrant/gunicorn.conf.py wsgi:application

