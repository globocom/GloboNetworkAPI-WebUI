Installing GloboNetworkAPI WebUI
#################################

Using pre-configured VM
************************

In order to use the pre-configured VM you need to have `vagrant <https://www.vagrantup.com/downloads.html>` and `VirtualBox <https://www.virtualbox.org/wiki/Downloads>` installed in your machine.

After that, go to the directory you want to install and do::

  git clone https://github.com/globocom/GloboNetworkAPI-WebUI
  cd GloboNetworkAPI-WebUI
  vagrant plugin install vagrant-omnibus
  vagrant up

After this you'll have the WebUI running on http://10.0.0.3:8080/

Installing from scratch
***********************

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
	gunicorn wsgi:application

Install CVS
*****************

You will need the JDK software in order to install CVS

::

	sudo yum install java-x-openjdk.x86_64

Set the JAVA_HOME variable with the path to java folder

::

	JAVA_HOME=/etc/java-x-openjdk.x86_64	

Download CVS software 

::

	sudo yum install cvs

Uncomment and set the variable CVS_JAVA_HOME  in cvs.sh

Run cvs

Put the following command in .bashrc

::

	export CVSROOT=:pserver:<user>@<host>:/<path>

Folder: ``GloboNetworkAPI-WebUI/Cadvlan/ACLS``::

	cvs checkout <repo>/ACLS

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

