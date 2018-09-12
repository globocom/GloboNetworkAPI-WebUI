# -*- coding:utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Django settings for CadVlan project.
import logging
import os
import sys

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

PDB = os.getenv('NETWORKAPI_PDB', '0') == '1'
DEBUG = os.getenv('NETWORKAPI_DEBUG', '0') == '1'
TEMPLATE_DEBUG = DEBUG
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

CADVLAN_VERSION = '11.11'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media"

STATIC_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'static'),
)

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nx@6034rdr+jh!0_*0j4ueqzd9#=a3h87jzl!xc@9x2l-1n4nv'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    "django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
    'CadVlan.processExceptionMiddleware.LoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

if PDB:
    MIDDLEWARE_CLASSES += (
        'django_pdb.middleware.PdbMiddleware',
    )

ROOT_URLCONF = 'CadVlan.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

if PDB:
    INSTALLED_APPS += (
        'django_pdb',
    )

PROJECT_APPS = (
    'CadVlan.AccessType',
    'CadVlan.Acl',
    'CadVlan.Auth',
    'CadVlan.BlockRules',
    'CadVlan.Environment',
    'CadVlan.EnvironmentVip',
    'CadVlan.EquipAccess',
    'CadVlan.EquipGroup',
    'CadVlan.EquipInterface',
    'CadVlan.EquipScript',
    'CadVlan.Equipment',
    'CadVlan.EquipmentType',
    'CadVlan.EventLog',
    'CadVlan.Filter',
    'CadVlan.GroupEquip',
    'CadVlan.GroupUser',
    'CadVlan.HealthcheckExpect',
    'CadVlan.Ldap',
    'CadVlan.Net',
    'CadVlan.NetworkType',
    'CadVlan.OptionVip',
    'CadVlan.Pool',
    'CadVlan.Rack',
    'CadVlan.Script',
    'CadVlan.ScriptType',
    'CadVlan.System',
    'CadVlan.User',
    'CadVlan.UserGroup',
    'CadVlan.Util',
    'CadVlan.VipRequest',
    'CadVlan.Vlan',
    'CadVlan.Vrf'
)

INSTALLED_APPS += PROJECT_APPS

SESSION_ENGINE = (
    'django.contrib.sessions.backends.file'
)

SESSION_COOKIE_NAME = 'cadvlan.globo.com'
SESSION_COOKIE_AGE = 0
SESSION_EXPIRY_AGE = 0
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211'
        ]
    }
}

CACHE_ENVIRONMENTS_TIMEOUT = 900
CACHE_EQUIPMENTS_TIMEOUT = 900  # Values in seconds
CACHE_VLANS_TIMEOUT = 300  # Values in seconds

URL_LOGIN = '/login'
URL_HOME = '/home'

NETWORK_API_URL = os.getenv('NETWORK_API_URL', 'http://10.0.0.2:8000/')
NETWORK_API_USERNAME = 'CadVlan'
NETWORK_API_PASSWORD = '12345678'

# Configurações de Email
EMAIL_FROM = 'globo@s2it.com.br'
EMAIL_HOST = 'pod51028.outlook.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'globo@s2it.com.br'
EMAIL_HOST_PASSWORD = '123$mudar'
EMAIL_USE_TLS = True

MAX_RESULT_DEFAULT = 25  # Options-> 10, 25, 50, 100

PATCH_PANEL_ID = 8

PATH_ACL = os.path.join(PROJECT_ROOT_PATH, 'ACLS/')

PATH_PERMLISTS = os.path.join(PROJECT_ROOT_PATH, 'permissions')

CACERTDIR = '/etc/pki/globocom/'
LDAP_DC = "dc=dcgit,dc=com"
LDAP_SSL = False
LDAP_INITIALIZE = "ldap.address.com:389"
LDAP_INITIALIZE_SSL = "ldap.address.com:636"
LDAP_CREDENTIALS_USER = "ldap_user"
LDAP_CREDENTIALS_PASSWORD = "ldap_password"
LDAP_MANAGER_USER = "ldap_user"
LDAP_MANAGER_PASSWORD = "ldap_password"
LDAP_PASSWORD_DEFAULT_HASH = "{MD5}a5BE2fasdfwUZ8q82LTDvcQ=="
LDAP_PASSWORD_DEFAULT = "ldap_password_default"

ACCESS_EXTERNAL_TTL = 1800  # Values in seconds

SECRET_KEY = '12345678'  # Generates key encryption

LOG_FILE = PROJECT_ROOT_PATH + '/log.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(message)s',
            'datefmt': '%d/%b/%Y:%H:%M:%S %z',
        },
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s - M:%(module)s, P:%(process)d, T:%(thread)d, MSG:%(message)s',
            'datefmt': '%d/%b/%Y:%H:%M:%S %z',
        },
    },
    'handlers': {
        'handlers-request': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'simple',
            'mode': 'a',
        },
        'handlers-view': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'verbose',
            'mode': 'a',
        },
    },
    'loggers': {
        'default': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'networkapiclient': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Util': {
            'handlers': ['handlers-request'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Auth': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Script': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.ScriptType': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.EquipAccess': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.OptionVip': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.EnvironmentVip': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.GroupEquip': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.EquipGroup': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.GroupUser': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.UserGroup': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Acl': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.AccessType': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.EquipmentType': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.NetworkType': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.HealthcheckExpect': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.VipRequest': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Ldap': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.EventLog': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Vlan': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.BlockRules': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'CadVlan.Pool': {
            'handlers': ['handlers-view'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
reload(sys)
sys.setdefaultencoding('utf-8')
