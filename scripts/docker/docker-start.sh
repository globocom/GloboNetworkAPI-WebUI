# Waits for other containers availability
sleep 5

# Resolves the networkapi container IP and sets it on the /etc/hosts
NETAPI_IP=$(nslookup netapi_app | grep Address | tail -1 | awk '{print $2}')
printf "$NETAPI_IP\tnetworkapi.docker\n" >> /etc/hosts

echo -e "PYTHONPATH=\"/netapi_webui/networkapi_webui:/netapi_webui/$PYTHONPATH\"" >> /etc/environment

cat > /etc/init.d/gunicorn_networkapi_webui <<- EOM
#!/bin/bash
### BEGIN INIT INFO
# Provides:          scriptname
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

/usr/local/bin/gunicorn -c /netapi_webui/gunicorn.conf.py wsgi:application --reload
EOM

chmod 777 /etc/init.d/gunicorn_networkapi_webui
update-rc.d gunicorn_networkapi_webui defaults
export PYTHONPATH="/netapi_webui/networkapi_webui:/netapi_webui/$PYTHONPATH"


# Use NetworkAPI python client library locally
[ ! -d "GloboNetworkAPI-client-python" ] && {
    git clone https://github.com/globocom/GloboNetworkAPI-client-python.git
}

# Update and install as development package
cd GloboNetworkAPI-client-python
git pull origin master
python setup.py develop
cd ..


echo "starting gunicorn"
/etc/init.d/gunicorn_networkapi_webui start

touch /tmp/gunicorn-globonetworkapi_webui_error.log
tail -f /tmp/gunicorn-globonetworkapi_webui_error.log