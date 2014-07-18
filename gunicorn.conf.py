import os

#Chooses the number of workers accordingly to the number os CPU cores
def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")

try:
    import multiprocessing
    workers = multiprocessing.cpu_count() * 2 + 1
except ImportError:
	workers = numCPUs() * 2 + 1
	pass

#Configure your log directory
LOGDIR = "/tmp/"

PIDFILE = "%s/gunicorn-cadvlan.pid" % LOGDIR
accesslog = "%s/gunicorn-cadvlan_access.log" % LOGDIR
errorlog = "%s/gunicorn-cadvlan_error.log" % LOGDIR
loglevel = "debug"

#Choose user/group to run the server if daemon=true
daemon = True
#user="www-data"
#group="www-data"

#IP and Port to listen
<<<<<<< HEAD
bind = "0.0.0.0:8000"
=======
bind = "0.0.0.0:8080"
>>>>>>> 25f112b9aed951ce755bae831ad8c174a65c02d7

backlog = 2048
preload_app = True
pidfile = PIDFILE
<<<<<<< HEAD
=======

>>>>>>> 25f112b9aed951ce755bae831ad8c174a65c02d7
