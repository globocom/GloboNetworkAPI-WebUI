Installing GloboNetworkAPI WebUI
#################################

Following examples were based on CentOS 7.0.1406 installation.

All root passwords were configured to "default".

Create a specific User/Group
****************************

::

	useradd -m -U webui 
	passwd webui
	visudo
		webui      ALL=(ALL)       ALL

	sudo mkdir /opt/app/
	sudo chmod 777 /opt/app/


Download Code
*************

Download GloboNetworkAPI code from `Globocom GitHub <https://github.com/globocom/GloboNetworkAPI-WebUI>`_.

In this example we are downloading code to ``/opt/app/``::

	sudo yum install git
	cd /opt/app/
	git clone https://github.com/globocom/GloboNetworkAPI-WebUI

We are exporting this variable below to better document the install process::

	export WEBUI_FOLDER=/opt/app/GloboNetworkAPI-WebUI/
	echo "export WEBUI_FOLDER=/opt/app/GloboNetworkAPI-WebUI/" >> ~/.bashrc 


Create a VirtualEnv
*******************

::

	sudo yum install python-virtualenv
	sudo easy_install pip
	virtualenv ~/virtualenvs/webui_env
	source ~/virtualenvs/webui_env/bin/activate
	echo "source ~/virtualenvs/webui_env/bin/activate" >> ~/.bashrc 


Install Dependencies 
***************************

You will need the following packages in order to install the next python packages via ``pip``::

	sudo yum install gcc
	yum install openldap-devel
	
Install the packages listed on ``$WEBUI_FOLDER/requirements.txt`` file:

::

	pip install -r $WEBUI_FOLDER/requirements.txt

Create a ``sitecustomize.py`` inside your ``/path/to/lib/python2.X`` folder with the following content::

	import sys
	sys.setdefaultencoding('utf-8')

::

	echo -e "import sys\nsys.setdefaultencoding('utf-8')\n" > ~/virtualenvs/webui_env/lib/python2.7/sitecustomize.py


Install Memcached
*****************

You can run memcached locally or you can set file variable ``CACHES{default{LOCATION`` to use a remote memcached farm in file ``$WEBUI_FOLDER/settings.py``.

In case you need to run locally::
	
	sudo yum install memcached
	sudo systemctl start memcached
	sudo systemctl enable memcached

HTTP Server Configuration
*************************

For a better performance, install Green Unicorn to run NetworkAPI.

::

	pip install gunicorn

There is no need to install a nginx or apache to proxy pass the requests, once there is no static files in the API.

Edit ``$WEBUI_FOLDER/gunicorn.conf.py`` to use your log files location and `user preferentes <http://gunicorn-docs.readthedocs.org/en/latest/settings.html#config-file>`_ and run gunicorn::

	cd $WEBUI_FOLDER/
	gunicorn cadvlan_wsgi:application

Test installation
*****************

Try to access the root location of the API::

	http://your_location:8080/

This should take you the login page.

LDAP Server Configuration
*************************

If you want to use LDAP authentication, configure the following variables in ``FILE``:

!TODO

Working with Documentation
**************************

If you want to generate documentation, you need the following python modules installed::

	pip install sphinx==1.2.2
	pip install sphinx-rtd-theme==0.1.6
	pip install pytest==2.2.4
