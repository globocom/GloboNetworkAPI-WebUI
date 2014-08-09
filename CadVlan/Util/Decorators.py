# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Util.Json import Json
from CadVlan.Util.utility import get_param_in_request
from CadVlan.VipRequest.encryption import Encryption
from CadVlan.forms import ControlAcessForm
from CadVlan.messages import auth_messages
from CadVlan.settings import URL_HOME, URL_LOGIN, NETWORK_API_URL
from CadVlan.templates import TOKEN_INVALID
from networkapiclient.ClientFactory import ClientFactory
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from hashlib import sha1
import json
import logging
import time
import re

logger = logging.getLogger(__name__)

AJAX = 'AJAX'
LOCK = 'LOCK'
TOKEN = 'token'


def login_required(view_func):
    '''
    Validates that the user is logged
    '''
    def _decorated(request, *args, **kwargs):

        auth = AuthSession(request.session)

        if auth.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:

            if request.is_ajax():
                response = HttpResponseRedirect(URL_LOGIN)
                response.status_code = 278

                return response

            ajax = request.META.get(AJAX)

            if ajax is not None and ajax == 1:
                return HttpResponse(json.dumps(Json(None, True, URL_LOGIN).__dict__))

            else:
                return HttpResponseRedirect(URL_LOGIN + '?redirect=' + request.path)

    return _decorated


def has_perm(permission):
    '''
    Validates that the user has access permission

    :param permission: access permission to be validated
    :param write: permission be write
    :param read: permission be read
    '''
    def _decorated(view_func):

        def _has_perm(request, *args, **kwargs):

            auth = AuthSession(request.session)

            if auth.is_authenticated():

                user = auth.get_user()

                for perm in permission:
                    write = perm['write'] if perm.has_key("write") else None
                    read = perm['read'] if perm.has_key("read") else None
                    if not user.has_perm(perm['permission'], write, read):
                        messages.add_message(
                            request, messages.ERROR, auth_messages.get('user_not_authorized'))
                        return HttpResponseRedirect(URL_HOME)

                return view_func(request, *args, **kwargs)

            else:
                return HttpResponseRedirect(URL_LOGIN)

        return _has_perm

    return _decorated


def log(view_func):
    '''
    Logs all requests
    '''
    def _decorated(request, *args, **kwargs):

        post_data = request.raw_post_data
        post_data = re.sub(r'password=(.*?)&', 'password=****&', post_data)
        post_data = re.sub(r'new_pass=(.*?)&', 'new_pass=****&', post_data)
        post_data = re.sub(
            r'confirm_new_password=(.*?)$', 'confirm_new_password=****', post_data)

        logger.info(u'Start of the request[%s] for URL[%s] with DATA[%s].' % (
            request.method, request.path, post_data))

        return view_func(request, *args, **kwargs)

    return _decorated


def access_external():
    '''
    Controls access external request vip form with token stored in memcached
    '''
    def _decorated(func):

        def _control(request, *args, **kwargs):

            key = get_param_in_request(request, TOKEN)

            is_valid = True
            if key is not None:

                # Search in cache if it exists
                if cache.has_key(key):

                    # Get hash in cache
                    hash = cache.get(key)

                    # Decrypt hash
                    user = Encryption().Decrypt(hash)

                    username, password, user_ldap = str(user).split("@")

                    if user_ldap == "":
                        client = ClientFactory(
                            NETWORK_API_URL, username, password)
                    else:
                        client = ClientFactory(
                            NETWORK_API_URL, username, password, user_ldap)
                else:
                    is_valid = False

            # If it is not valid  mount of return depending on the type of
            # request
            if not is_valid:

                msg = auth_messages.get("token_invalid")

                if request.is_ajax():
                    return HttpResponse(msg, status=203)

                else:

                    return HttpResponse(loader.render_to_string(TOKEN_INVALID, {"error": msg}), status=200)

            kwargs["form_acess"] = ControlAcessForm(initial={"token": key})
            kwargs["client"] = client

            # Execute method
            return func(request, *args, **kwargs)

        return _control

    return _decorated


def cache_function(length):
    """
    Cache the result of function

    :param length: time in seconds to stay in cache
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
