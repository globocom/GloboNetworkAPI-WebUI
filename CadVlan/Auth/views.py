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


from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib import messages
from CadVlan.settings import NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD, URL_HOME, URL_LOGIN, SESSION_EXPIRY_AGE, EMAIL_FROM, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from CadVlan import templates
from CadVlan.Util.Decorators import login_required, log
from CadVlan.messages import auth_messages
from CadVlan.Auth.models import User
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Auth.forms import LoginForm, PassForm, ChangePassForm
from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.exception import InvalidParameterError, NetworkAPIClientError
from CadVlan.Util.utility import make_random_password
from CadVlan.templates import MAIL_NEW_PASS, AJAX_NEW_PASS
from django.core.mail import EmailMessage
from django.template import loader
import logging
from CadVlan.Util.shortcuts import render_to_response_ajax

from CadVlan.Ldap.model import Ldap, LDAPNotFoundError
import re
import hashlib
import base64
from django.core.mail.backends.smtp import EmailBackend

logger = logging.getLogger(__name__)


@log
def login(request):

    modal_auto_open = "false"

    if request.method == 'POST':

        form = LoginForm(request.POST)
        form_pass = PassForm()

        if form.is_valid():

            try:

                client = ClientFactory(
                    NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD)

                user = client.create_usuario().authenticate(form.cleaned_data[
                    'username'], form.cleaned_data['password'], form.cleaned_data['is_ldap_user'])

                if user is None:
                    messages.add_message(
                        request, messages.ERROR, auth_messages.get("user_invalid"))

                else:

                    request.session.set_expiry(SESSION_EXPIRY_AGE)

                    auth = AuthSession(request.session)

                    user = user.get('user')

                    if user.get('permission') is None:
                        messages.add_message(
                            request, messages.ERROR, auth_messages.get("nogroup_error"))
                        return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

                    auth.login(User(user.get('id'), user.get('user'), user.get('nome'), user.get(
                        'email'), user.get('pwd'), user.get('permission'), user.get('ativo'), user.get('user_ldap')))

                    if form.cleaned_data['redirect'] != "":
                        return HttpResponseRedirect(form.cleaned_data['redirect'])

                    return HttpResponseRedirect(URL_HOME)

            except InvalidParameterError, e:
                logger.error(e)
                messages.add_message(
                    request, messages.ERROR, auth_messages.get("user_invalid"))

            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

            except LDAPNotFoundError, e:
                logger.error(e)
                messages.add_message(
                    request, messages.ERROR, auth_messages.get("user_ldap_not_found"))

            except Exception, e:
                logger.error(e)
                user = {}
                messages.add_message(
                    request, messages.ERROR, auth_messages.get("500"))

            return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

        else:
            return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

    else:

        auth = AuthSession(request.session)

        if auth.is_authenticated():
            return HttpResponseRedirect(URL_HOME)

        form = LoginForm()
        form_pass = PassForm()

        if request.GET is not None:
            form.fields['redirect'].initial = request.GET.get('redirect')

        return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

@log
def logout(request):
    auth = AuthSession(request.session)
    auth.logout()
    return HttpResponseRedirect(URL_LOGIN)

@log
def handler404(request):
    auth = AuthSession(request.session)

    messages.add_message(
        request, messages.ERROR, auth_messages.get("404") % request.path)

    if auth.is_authenticated():
        return HttpResponseRedirect(URL_HOME)

    return HttpResponseRedirect(URL_LOGIN)

@log
def handler500(request):
    auth = AuthSession(request.session)

    messages.add_message(request, messages.ERROR, auth_messages.get("500"))

    if auth.is_authenticated():
        return HttpResponseRedirect(URL_HOME)

    return HttpResponseRedirect(URL_LOGIN)

@log
@login_required
def home(request):
    return render_to_response(templates.HOME, context_instance=RequestContext(request))

@log
def lost_pass(request):
    form = LoginForm()
    modal_auto_open = "true"

    try:

        if request.method == 'POST':

            form_pass = PassForm(request.POST)

            if form_pass.is_valid():

                client = ClientFactory(
                    NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD)
                users = client.create_usuario().listar()
                users = users.get("usuario")

                username = form_pass.cleaned_data['username']
                email = form_pass.cleaned_data['email']

                for user in users:
                    if user.get("user").upper() == username.upper():
                        if user.get("email") == email:

                            if not user.get('user_ldap'):
                                pass_open = make_random_password()
                                password = hashlib.md5(pass_open).hexdigest()

                                ativo = None

                                if user.get('ativo'):
                                    ativo = '1'
                                else:
                                    ativo = '0'

                                client.create_usuario().alterar(user.get('id'), user.get('user'), password,
                                                                user.get('nome'), ativo, user.get('email'), user.get('user_ldap'))

                                lists = dict()
                                lists['user'] = user.get('user')
                                lists['new_pass'] = pass_open

                                # Montar Email com nova senha
                                connection = EmailBackend(
                                    username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
                                send_email = EmailMessage('Solicitação de Nova Senha', loader.render_to_string(
                                    MAIL_NEW_PASS, lists), EMAIL_FROM, [email], connection=connection)
                                send_email.content_subtype = "html"
                                send_email.send()

                                messages.add_message(
                                    request, messages.SUCCESS, auth_messages.get("email_success"))
                                modal_auto_open = 'false'
                                return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))
                            else:
                                messages.add_message(
                                    request, messages.ERROR, auth_messages.get("user_ldap_cant_recover_pass"))
                                modal_auto_open = 'false'
                                return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

                for user in users:
                    if user.get("user_ldap") is not None and user.get("user_ldap").upper() == username.upper():
                        messages.add_message(
                            request, messages.ERROR, auth_messages.get("user_ldap_cant_recover_pass"))
                        modal_auto_open = 'false'
                        return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

                messages.add_message(
                    request, messages.ERROR, auth_messages.get("user_email_invalid"))
                modal_auto_open = 'false'

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        modal_auto_open = 'false'
    except BaseException, e:
        logger.exception(e)
        logger.error("URLError Invalid EMAIL_HOST in settings.py")
        messages.add_message(
            request, messages.ERROR, "Invalid EMAIL_HOST in settings.py")
        modal_auto_open = 'false'

    return render_to_response(templates.LOGIN, {'form': form, 'form_pass': form_pass, 'modal': modal_auto_open}, context_instance=RequestContext(request))

@log
@login_required
def change_password(request):

    lists = dict()

    if request.method == 'GET':

        lists['change_pass_form'] = ChangePassForm()
        return render_to_response_ajax(AJAX_NEW_PASS, lists, context_instance=RequestContext(request))

    if request.method == 'POST':

        change_pass_form = ChangePassForm()

        try:

            change_pass_form = ChangePassForm(request.POST)

            if change_pass_form.is_valid():

                auth = AuthSession(request.session)
                client = auth.get_clientFactory()

                new_password = change_pass_form.cleaned_data['new_pass']
                user = auth.get_user()
                user_id = user.get_id()
                user_current_password = user.get_password()

                client.create_usuario().change_password(
                    user_id, user_current_password, new_password)
                user.set_password(new_password)

                messages.add_message(
                    request, messages.SUCCESS, auth_messages.get("pass_change_sucess"))

                # Returns HTML
                response = HttpResponse(loader.render_to_string(
                    AJAX_NEW_PASS, lists, context_instance=RequestContext(request)))
                # Send response status with error
                response.status_code = 200
                return response

            else:

                lists['change_pass_form'] = change_pass_form
                # Returns HTML
                response = HttpResponse(loader.render_to_string(
                    AJAX_NEW_PASS, lists, context_instance=RequestContext(request)))
                # Send response status with error
                response.status_code = 412
                return response

        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

            lists['change_pass_form'] = change_pass_form
            return render_to_response_ajax(AJAX_NEW_PASS, lists, context_instance=RequestContext(request))

#temporario
@log
@login_required
def menu(request):
    return render_to_response(templates.MENU, {'form': {}}, context_instance=RequestContext(request))

@log
@login_required
def header(request):
    return render_to_response(templates.HEADER, context_instance=RequestContext(request))
