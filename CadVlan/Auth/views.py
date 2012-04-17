# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.views.decorators.cache import cache_page
from CadVlan.settings import NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD, URL_HOME, URL_LOGIN, SESSION_EXPIRY_AGE, CACHE_TIMEOUT, EMAIL_FROM, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from CadVlan import templates
from CadVlan.Util.Decorators import login_required, log
from CadVlan.messages import auth_messages
from CadVlan.Auth.models import User
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.Auth.forms import LoginForm, PassForm
from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.exception import InvalidParameterError, NetworkAPIClientError
from CadVlan.Util.utility import make_random_password
from CadVlan.templates import MAIL_NEW_PASS
from django.core.mail import send_mail,EmailMessage,SMTPConnection
from django.template import loader

import logging

logger = logging.getLogger(__name__)

@log
def login(request):
    
    modal_auto_open = "false"

    if request.method == 'POST':

        form = LoginForm(request.POST)
        form_pass = PassForm()
        

        if form.is_valid():

                try:

                    client = ClientFactory(NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD)
                    user = client.create_usuario().authenticate(form.cleaned_data['username'], form.cleaned_data['password'])

                    if user is None:
                        messages.add_message(request, messages.ERROR, auth_messages.get("user_invalid"))

                    else:

                        request.session.set_expiry(SESSION_EXPIRY_AGE)

                        auth = AuthSession(request.session)
                        #auth.login(User(**user.get('user')))

                        user = user.get('user')
                        auth.login(User(user.get('id'), user.get('user'), user.get('nome'), user.get('email'), user.get('pwd'), user.get('permission'), user.get('ativo')))

                        if form.cleaned_data['redirect'] != "" :
                            return HttpResponseRedirect(form.cleaned_data['redirect'])

                        return HttpResponseRedirect(URL_HOME)

                except InvalidParameterError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, auth_messages.get("user_invalid"))

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e )

                return render_to_response(templates.LOGIN, {'form': form ,'form_pass':form_pass,'modal':modal_auto_open}, context_instance=RequestContext(request))

        else:
            return render_to_response(templates.LOGIN, {'form': form ,'form_pass':form_pass,'modal':modal_auto_open}, context_instance=RequestContext(request))

    else:

        auth = AuthSession(request.session)

        if auth.is_authenticated():
            return HttpResponseRedirect(URL_HOME)

        form = LoginForm()
        form_pass = PassForm()

        if request.GET is not None:
            form.fields['redirect'].initial = request.GET.get('redirect')

        return render_to_response(templates.LOGIN, {'form': form ,'form_pass':form_pass,'modal':modal_auto_open}, context_instance=RequestContext(request))

@log
def logout(request):
    auth = AuthSession(request.session)
    auth.logout()
    return HttpResponseRedirect(URL_LOGIN);

@log
def handler404(request):
    auth = AuthSession(request.session)

    messages.add_message(request, messages.ERROR, auth_messages.get("404") % request.path)

    if auth.is_authenticated():
        return HttpResponseRedirect(URL_HOME)

    return HttpResponseRedirect(URL_LOGIN);

@log
def handler500(request):
    auth = AuthSession(request.session)

    messages.add_message(request, messages.ERROR, auth_messages.get("500"))

    if auth.is_authenticated():
        return HttpResponseRedirect(URL_HOME)

    return HttpResponseRedirect(URL_LOGIN);

@log
@login_required
@cache_page(CACHE_TIMEOUT)
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
            
                client = ClientFactory(NETWORK_API_URL, NETWORK_API_USERNAME, NETWORK_API_PASSWORD)
                users = client.create_usuario().listar()
                users = users.get("usuario")
            
                username = form_pass.cleaned_data['username']
                email = form_pass.cleaned_data['email']
            
                for user in users:
                    if user.get("user").upper() == username.upper():
                        if user.get("email") == email:
                            
                            password = make_random_password()
                            
                            ativo = None
                            
                            if user.get('ativo'):
                                ativo = '1'
                            else:
                                ativo = '0'
                            
                            client.create_usuario().alterar(user.get('id'), user.get('user'), password, user.get('nome'), ativo, user.get('email')) 
                            
                            
                            lists = dict()
                            lists['user'] = user.get('user')
                            lists['new_pass'] = password
                            
                            #Montar Email com nova senha
                            
                            
                            connection = SMTPConnection(username = EMAIL_HOST_USER, password = EMAIL_HOST_PASSWORD)
                            send_email = EmailMessage('Solicitação de Nova Senha',  loader.render_to_string(MAIL_NEW_PASS, lists) ,EMAIL_FROM, [email], connection = connection)
                            send_email.content_subtype = "html"
                            send_email.send()
                        
                            
                            messages.add_message(request, messages.SUCCESS, auth_messages.get("email_success"))
                            modal_auto_open = 'false'
                            return render_to_response(templates.LOGIN, {'form': form ,'form_pass':form_pass,'modal':modal_auto_open}, context_instance=RequestContext(request))
            
            
                messages.add_message(request, messages.ERROR, auth_messages.get("user_email_invalid"))
                modal_auto_open = 'false'
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e )
        modal_auto_open = 'false'
            
            
    return render_to_response(templates.LOGIN, {'form': form ,'form_pass':form_pass,'modal':modal_auto_open}, context_instance=RequestContext(request))
        