# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.User.forms import UserForm
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import make_random_password, validates_dict
from CadVlan.forms import DeleteForm
from CadVlan.messages import user_messages, error_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_FROM
from CadVlan.templates import USER_LIST, MAIL_NEW_USER
from django.conf.urls.defaults import url
from django.contrib import messages
from django.core.mail import SMTPConnection
from django.core.mail.message import EmailMessage
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError
import logging

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def list_all(request,id_user,status):
    
    lists = dict()
    edit = False if id_user == "0" else True
    lists['open_form'] = "True" if edit or status == "1"  else "False"
    lists['edit'] = str(edit)
    lists['id_user'] = id_user
    lists['action_new_users'] =  reverse("user.form", args=[0 ,0])
    
    try:
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        # Get all users from NetworkAPI
       
        groups = client.create_grupo_usuario().listar()
        lists['form'] = DeleteForm()
        lists['form_user'],lists['action'] = create_form_user(id_user,client,groups,edit)
        
        if request.method == 'POST':
            
            form = UserForm(groups,request.POST)
            lists['form_user'] = form
            
            if form.is_valid():
                
                if edit:
                    
                    edit_user(form,client,id_user) 
                    messages.add_message(request, messages.SUCCESS, user_messages.get("success_edit"))
                    
                    
                else:
                    
                    save_user(form,client)
                    messages.add_message(request, messages.SUCCESS, user_messages.get("success_insert"))
                
                lists['form_user'] = create_form_user(0,client,groups,False)
                lists['open_form'] = "False"
            
            else:
                lists['open_form'] = 'True'
                
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists['users'] = list_user(client)

    return render_to_response(USER_LIST, lists, context_instance=RequestContext(request))

def list_user(client):
    users = client.create_usuario().list_with_usergroup() 
    users = validates_dict(users,'usuario')     
    for user in users:
        if user['grupos'] is not None and type(user['grupos']) != list:
            user['grupos'] = [user['grupos']]
                          
    return users
    
def create_form_user(id_user,client,groups,edit):
    
    if edit:
        user = client.create_usuario().get_by_id(id_user).get('usuario')
        form_user = UserForm(groups,initial = {"name":user['nome'],"email":user['email'],"user":user['user'],"groups":user['grupos'],"password":user['pwd'],"active":user['ativo']})
        #action = "user.edit %s 1" % (str(id_user))
        action = url("user.edit",id_user,1)
    else:
        #action = "user.edit 0 0"
        action = url("user.edit",0,0)
        form_user = UserForm(groups)
        
    return form_user,action

def save_user(form,client):
    
    list_mail = dict()
    
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    user = form.cleaned_data['user'].upper()
    groups = form.cleaned_data['groups']
    
    list_mail['nome'] = name
    list_mail['user'] = user
    
    password = make_random_password()
    list_mail['pass'] = password
    
    new_user = client.create_usuario().inserir(user, password, name, email)
    
    for group in groups:
        client.create_usuario_grupo().inserir(new_user.get('usuario')['id'], group)
    
    connection = SMTPConnection(username = EMAIL_HOST_USER, password = EMAIL_HOST_PASSWORD)
    send_email = EmailMessage('Novo Usuário CadVlan-Globo.com',  loader.render_to_string(MAIL_NEW_USER, list_mail) ,EMAIL_FROM, [email], connection = connection)
    send_email.content_subtype = "html"
    send_email.send()
   
def edit_user(form,client,id_user):
    
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    user = form.cleaned_data['user']
    groups_new = form.cleaned_data['groups']
    pwd = form.cleaned_data['password']
    ativo = 1 if form.cleaned_data['active'] else 0
    
    groups = client.create_usuario().get_by_id(id_user).get('usuario')['grupos']
    
    if groups is not None:
        for group in groups:
            client.create_usuario_grupo().remover(id_user, group)
        
    for group in groups_new:
        client.create_usuario_grupo().inserir(id_user, group)
    
    client.create_usuario().alterar(id_user, user.upper(), pwd, name, ativo, email)
    
@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def delete_all(request):

    if request.method == 'POST':

        form = DeleteForm(request.POST)
        
        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_user = auth.get_clientFactory().create_usuario()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list() 

            # Control others exceptions
            have_errors = False

            # For each user selected to remove
            for id_user in ids:
                try:

                    # Execute in NetworkAPI
                    user = client_user.get_by_id(id_user).get('usuario')
                    client_user.alterar(user.get("id"), user.get("user"), user.get("pwd"), user.get('nome'), 0, user.get('email'))

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove nothing
            if len(error_list) == len(ids):
                messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_all"))

            # If cant remove someones
            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, user_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.ERROR, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('user.list',0,0)