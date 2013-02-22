# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: tromero / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Ldap.views import get_groups
from CadVlan.Ldap.model import Ldap, LDAPError
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.User.forms import UserForm
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import make_random_password, validates_dict
from CadVlan.forms import DeleteForm
from CadVlan.messages import user_messages, error_messages
from CadVlan.permissions import ADMINISTRATION, ENVIRONMENT_VIP
from CadVlan.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_FROM
from CadVlan.templates import USER_LIST, MAIL_NEW_USER, AJAX_LDAP_USERS_BY_GROUP, AJAX_LDAP_USER_POP_NAME_MAIL,\
    AJAX_AUTOCOMPLETE_LIST
from django.http import HttpResponse
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
from CadVlan.Equipment.business import list_users
from CadVlan.Util.shortcuts import render_to_response_ajax

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_ldap_pop_name_mail(request, cn):
    try:
        
        lists = dict()
        
        # Get user
        auth = AuthSession(request.session)
        ldap_user = Ldap(auth).get_user(cn)
        lists['ldap_name'] = ldap_user['givenName']+ ' '+ldap_user['initials']+' '+ldap_user['sn']
        lists['ldap_email'] = ldap_user['mail']
        lists['error'] = ' '
        
        response = HttpResponse(loader.render_to_string(AJAX_LDAP_USER_POP_NAME_MAIL, lists, context_instance=RequestContext(request)))
        #render_to_response_ajax(AJAX_LDAP_USER_POP_NAME_MAIL, lists, context_instance=RequestContext(request))
        response.status_code = 200
        return response
        
    except LDAPError:
        lists['ldap_name'] = ' '
        lists['ldap_email'] = ' '
        lists['error'] = 'O LDAP não está disponível, não será possível associar o usuário CadVlan a um usuário do LDAP.'

    response = HttpResponse(loader.render_to_string(AJAX_LDAP_USER_POP_NAME_MAIL, lists, context_instance=RequestContext(request)))
    response.status_code = 278
    return response

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def ajax_ldap_users_by_group(request, ldap_group, id_user):
    try:
        
        lists = dict()
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        exclude_list = []
        user_list = client.create_usuario().listar().get('usuario')
        for usr in user_list:
            if usr['user_ldap'] is not None and usr['user_ldap'] != '' and usr['id'] != id_user:
                exclude_list.append(usr['user_ldap'])
            
        ldap_users = Ldap(auth).get_users_group(ldap_group, exclude_list)
        lists['ldap_users'] = ldap_users
        
        # Returns HTML
        response = HttpResponse(loader.render_to_string(AJAX_LDAP_USERS_BY_GROUP, lists, context_instance=RequestContext(request)))
        response.status_code = 200
        return response
        
    except LDAPError:
        lists['error'] = 'O LDAP não está disponível, não será possível associar o usuário CadVlan a um usuário do LDAP.'
    
    # Returns HTML
    response = HttpResponse(loader.render_to_string(AJAX_LDAP_USERS_BY_GROUP, lists, context_instance=RequestContext(request)))
    # Send response status with error
    response.status_code = 278
    return response

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def list_all(request,id_user,status):
    
    lists = dict()
    edit = False if id_user == "0" else True
    lists['open_form'] = "True" if edit or status == "1" else "False"
    lists['edit'] = str(edit)
    lists['id_user'] = id_user
    lists['action_new_users'] =  reverse("user.form", args=[0 ,0])
    
    try:
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        # Get all users from NetworkAPI
        
        try:
            ldap_groups_ = get_groups(Ldap(auth))
            ldap_groups = [(ldap_grp['gidNumber'], ldap_grp['cn']) for ldap_grp in ldap_groups_]
            ldap_up = True
        except LDAPError:
            messages.add_message(request, messages.ERROR, user_messages.get("ldap_offline"))
            ldap_up = False
            ldap_groups_ = None
            ldap_groups = None
            
        lists['ldap_up'] = ldap_up
        
        groups = client.create_grupo_usuario().listar()
        lists['ldap_groups'] = ldap_groups_
        lists['form'] = DeleteForm()
        lists['form_user'], lists['action'] = create_form_user(id_user,auth,groups,edit, ldap_groups)
        
        if request.method == 'POST':
            
            try:
                ldap_grp = int(request.POST['ldap_group'])
            except:
                ldap_grp = 0
            
            if ldap_grp > 0 and ldap_up:
                list_users_ldap = Ldap(auth).get_users_group(ldap_grp)
            else:
                list_users_ldap = None
            
            form = UserForm(groups, ldap_groups, list_users_ldap, request.POST)
            lists['form_user'] = form
            
            if form.is_valid():
                
                if edit:
                    
                    edit_user(form,client,id_user) 
                    messages.add_message(request, messages.SUCCESS, user_messages.get("success_edit"))
                    
                else:
                    
                    save_user(form,client)
                    messages.add_message(request, messages.SUCCESS, user_messages.get("success_insert"))
                
                lists['form_user'] ,lists['action'] = create_form_user(0,auth,groups,False, ldap_groups)
                lists['open_form'] = "False"
            
            else:
                lists['open_form'] = 'True'
                
        lists['users'] = list_user(client)
    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(USER_LIST, lists, context_instance=RequestContext(request))

def list_user(client):
    users = client.create_usuario().list_with_usergroup() 
    users = validates_dict(users,'usuario')     
    for user in users:
        if user['grupos'] is not None and type(user['grupos']) != list:
            user['grupos'] = [user['grupos']]
                          
    return users
    
def create_form_user(id_user,auth,groups, edit, ldap_grps=None):
    
    if edit:
        user = auth.get_clientFactory().create_usuario().get_by_id(id_user).get('usuario')
        
        #Get LDAP user and the first group associated
        is_ldap = False
        usr_list = None
        ini_grp = None
        if user['user_ldap'] is not None:
            ldap = Ldap(auth)
            ldap_user_ = ldap.get_user(user['user_ldap'])
            
            users_grps = ldap.get_groups_user(ldap_user_['cn'])
            
            ldap_ini_grps = [grp[1] for grp in ldap_grps]
            for grp in users_grps:
                if grp in ldap_ini_grps:
                    ini_grp = ldap_grps[ldap_ini_grps.index(grp)][0]
                    usr_list = ldap.get_users_group(ini_grp)
                    is_ldap = True
                    break
                    
        
        form_user = UserForm(groups, ldap_group_list=ldap_grps, ldap_user_list=usr_list, initial = {"name":user['nome'],"email":user['email'],"user":user['user'],"groups":user['grupos'],"password":user['pwd'],"active":user['ativo'], "is_ldap":is_ldap, "ldap_group":ini_grp, "ldap_user":user['user_ldap']})
        #action = "user.edit %s 1" % (str(id_user))
        action = url("user.edit",id_user,1)
    else:
        #action = "user.edit 0 0"
        action = url("user.edit",0,0)
        form_user = UserForm(groups, ldap_grps)
        
    return form_user,action

def save_user(form,client):
    
    list_mail = dict()
    
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    user = form.cleaned_data['user'].upper()
    groups = form.cleaned_data['groups']
    user_ldap = form.cleaned_data['ldap_user'] if form.cleaned_data['is_ldap'] else None
    
    list_mail['nome'] = name
    list_mail['user'] = user
    
    password = make_random_password()
    list_mail['pass'] = password
    
    new_user = client.create_usuario().inserir(user, password, name, email, user_ldap)
    
    for group in groups:
        client.create_usuario_grupo().inserir(new_user.get('usuario')['id'], group)
    
    if user_ldap is None:
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
    user_ldap = form.cleaned_data['ldap_user'] if form.cleaned_data['is_ldap'] else None
    
    groups = client.create_usuario().get_by_id(id_user).get('usuario')['grupos']
    
    client.create_usuario().alterar(id_user, user.upper(), pwd, name, ativo, email, user_ldap)
    
    to_add, to_rem = diff(groups, groups_new)
    for group in to_add:
        client.create_usuario_grupo().inserir(id_user, group)
    for group in to_rem:
        client.create_usuario_grupo().remover(id_user, group)
    
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
                    client_user.alterar(user.get("id"), user.get("user"), user.get("pwd"), user.get('nome'), 0, user.get('email'), user.get('user_ldap'))

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

def diff(old, new):
        
    to_add = list(set(new) - set(old))
    to_rem = list(set(old) - set(new))
    
    return to_add, to_rem



@log
@login_required
@has_perm([{"permission": ENVIRONMENT_VIP, "read": True}])
def ajax_autocomplete_users(request):
    try:
        
        user_list = dict()
        
        # Get user auth
        auth = AuthSession(request.session)
        user = auth.get_clientFactory().create_usuario()
        
        # Get list of equipments from cache
        user_list = list_users(user)
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except BaseException, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response_ajax(AJAX_AUTOCOMPLETE_LIST, user_list, context_instance=RequestContext(request))

