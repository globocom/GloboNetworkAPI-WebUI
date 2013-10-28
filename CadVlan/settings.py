# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

# Django settings for CadVlan project.

import os
PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

CADVLAN_VERSION = 9

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

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

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

TEMPLATE_CONTEXT_PROCESSORS =(
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'CadVlan.processExceptionMiddleware.LoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'CadVlan.Auth',
    'CadVlan.Util',
    'CadVlan.Script',
    'CadVlan.ScriptType',
    'CadVlan.EquipAccess',
    'CadVlan.Vlan',
    'CadVlan.OptionVip',
    'CadVlan.EnvironmentVip',
    'CadVlan.GroupEquip',
    'CadVlan.EquipGroup',
    'CadVlan.GroupUser',
    'CadVlan.UserGroup',
    'CadVlan.Acl',
    'CadVlan.AccessType',
    'CadVlan.EquipmentType',
    'CadVlan.NetworkType',
    'CadVlan.HealthcheckExpect',
    'CadVlan.Ldap',
    'CadVlan.EventLog',
    'CadVlan.BlockRules',
    
)

SESSION_ENGINE = (
    'django.contrib.sessions.backends.file'
)

SESSION_COOKIE_NAME = 'cadvlan.globo.com'
SESSION_COOKIE_AGE = 1800
SESSION_EXPIRY_AGE = 1800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211'
        ]
    }
}

CACHE_EQUIPMENTS_TIMEOUT = 900 # Values in seconds
CACHE_VLANS_TIMEOUT = 300 # Values in seconds

URL_LOGIN = '/login'
URL_HOME = '/home'

NETWORK_API_URL = 'http://192.168.24.33/'
NETWORK_API_USERNAME = 'CadVlan'
NETWORK_API_PASSWORD = '12345678'

# Configurações de Email
EMAIL_FROM = 'globo@s2it.com.br'
EMAIL_HOST = 'pod51028.outlook.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'globo@s2it.com.br'
EMAIL_HOST_PASSWORD = '123$mudar'
EMAIL_USE_TLS = True

MAX_RESULT_DEFAULT = 25 # Options-> 10, 25, 50, 100

PATCH_PANEL_ID = 8

PATH_ACL = os.path.join(PROJECT_ROOT_PATH, 'ACLS/')

PATH_PERMLISTS = os.path.join(PROJECT_ROOT_PATH, 'permissions')

CACERTDIR='/etc/pki/globocom/'
LDAP_DC = "dc=globoi,dc=com"
LDAP_SSL = True
LDAP_INITIALIZE = "192.168.24.14:389"
LDAP_INITIALIZE_SSL = "globoi.com:636"
LDAP_CREDENTIALS_USER = "ldapweb"
LDAP_CREDENTIALS_PWD = "senha"
LDAP_MANAGER_PWD = "senha"
LDAP_PWD_DEFAULT_HASH = "{MD5}a5FE2fqsjiUZ6q41LBDswQ=="
LDAP_PWD_DEFAULT = "globocom"

ACCESS_EXTERNAL_TTL = 1800 # Values in seconds

SECRET_KEY = '12345678' # Generates key encryption 

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
            'formatter': 'simple',
            'filename': LOG_FILE,
            'mode': 'a', #append+create
        },
        'handlers-view': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': LOG_FILE,
            'mode': 'a', #append+create
        },
    },
    'loggers': {
        'django': {
            'handlers':['handlers-view'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['handlers-view'],
            'propagate': True,
            'level': 'ERROR',
        },
        'CadVlan.Util': {
            'handlers': ['handlers-request'],
        },
        'CadVlan.Auth': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.Script': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.ScriptType': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.EquipAccess': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.OptionVip': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.EnvironmentVip': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.GroupEquip': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.EquipGroup': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.GroupUser': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.UserGroup': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.Acl': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.AccessType': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.EquipmentType': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.NetworkType': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.HealthcheckExpect': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.VipRequest': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.Ldap': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.EventLog': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.Vlan': {
            'handlers': ['handlers-view'],
        },
        'CadVlan.BlockRules': {
            'handlers': ['handlers-view'],
        },                
    }
}