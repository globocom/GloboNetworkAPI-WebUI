# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.core.cache import cache
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.messages import auth_messages
from CadVlan.settings import URL_HOME, URL_LOGIN
from CadVlan.Util.Json import Json
from hashlib import sha1
import logging
import json
import time

logger = logging.getLogger(__name__)

AJAX = 'AJAX'
LOCK = 'LOCK'

def login_required(view_func):
    '''
    Validates that the user is logged
    '''
    def _decorated(request, *args, **kwargs):
        
        auth = AuthSession(request.session)

        if auth.is_authenticated():
            return view_func(request,*args, **kwargs)
        else:

            if request.is_ajax():
                response = HttpResponseRedirect(URL_LOGIN)
                response.status_code = 278

                return response

            ajax = request.META.get(AJAX) 

            if ajax is not None and ajax == 1 :
                return HttpResponse(json.dumps(Json(None, True, URL_LOGIN).__dict__))

            else:
                return HttpResponseRedirect(URL_LOGIN + '?redirect=' + request.path )

    return _decorated

def has_perm(permission, write = None, read = None):
    '''
    Validates that the user has access permission
    
    @param permission: access permission to be validated
    @param write: permission be write
    @param read: permission be read
    '''
    def _decorated(view_func):

        def _has_perm(request, *args, **kwargs):

            auth = AuthSession(request.session)

            if auth.is_authenticated():

                user = auth.get_user()

                if user.has_perm(permission, write, read):
                    return view_func(request,*args, **kwargs);

                else:
                    messages.add_message(request, messages.ERROR, auth_messages.get('user_not_authorized'))
                    return HttpResponseRedirect(URL_HOME)

            else:
                return HttpResponseRedirect(URL_LOGIN)

        return _has_perm

    return _decorated

def log(view_func):
    '''
    Logs all requests
    '''
    def _decorated(request, *args, **kwargs):

        logger.info(u'Start of the request[%s] for URL[%s] with DATA[%s].' % (request.method, request.path, request.raw_post_data))

        return view_func(request,*args, **kwargs)

    return _decorated

def cache_function(length):
    """
    Cache the result of function
    
    @param length: time in seconds to stay in cache
    @param key: key to cache, if not passed, function name will be used
    """
    def _decorated(func):
        
        def _cache(*args, **kwargs):
            
            key = sha1(str(func.__module__) + str(func.__name__)).hexdigest()
            
            # Search in cache if it exists
            if cache.has_key(key):
                
                # Get value in cache
                value = cache.get(key)
                
                # If was locked
                if value == LOCK:
                    # Try until unlock
                    while value == LOCK:
                        time.sleep(1)
                        value = cache.get(key)
                
                # Return value of cache
                return value
            
            # If not exists in cache
            else:
                # Function can be called several times before it finishes and is put into the cache,
                # then lock it to others wait it finishes.
                cache.set(key, LOCK, length)
                
                # Execute method
                result = func(*args, **kwargs)
                
                # Set in cache the result of method
                cache.set(key, result, length)
                
                return result
            
        return _cache
    return _decorated