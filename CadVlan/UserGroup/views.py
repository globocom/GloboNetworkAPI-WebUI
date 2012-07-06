# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.UserGroup.forms import UserGroupForm, PermissionGroupForm
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import convert_string_to_boolean, convert_boolean_to_int, validates_dict
from CadVlan.forms import DeleteForm, DeleteFormAux
from CadVlan.messages import error_messages, user_group_messages, perm_group_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import USERGROUP_LIST
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError, PermissaoAdministrativaDuplicadaError
import logging

logger = logging.getLogger(__name__)

def load_list(request, lists, id_ugroup, tab):
    
    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['users'] = validates_dict(client.create_usuario().list_by_group(id_ugroup), 'users')

        if not 'ugroup' in lists: 
            lists['ugroup'] = client.create_grupo_usuario().search(id_ugroup).get('group_user')

        if not 'form_users' in lists:
            lists['form_users'] = UserGroupForm(client.create_usuario().list_by_group_out(id_ugroup))

        lists['perms'] = validates_dict(client.create_permissao_administrativa().list_by_group(id_ugroup), 'perms')

        if not 'form_perms' in lists:
            lists['form_perms'] = PermissionGroupForm()

        if not 'action_edit_perms' in lists:
            lists['action_edit_perms'] = reverse("user-group-perm.form", args=[id_ugroup])

        lists['form'] = DeleteForm()
        lists['form_aux'] = DeleteFormAux()
        lists['tab'] = '0' if tab == '0' else '1'
        
        lists['action_new_users'] =  reverse("user-group.form", args=[id_ugroup])
        lists['action_new_perms'] =  reverse("user-group-perm.form", args=[id_ugroup])

        #Suggestion Administrative Permission 
        list_suggestion_perm = []
        for perm in validates_dict(client.create_permissao_administrativa().listar(), 'permissao_administrativa'):

            function = perm.get('funcao')

            if not function in list_suggestion_perm:
                list_suggestion_perm.append(function)

        lists['suggestion_perm'] = list_suggestion_perm


    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return lists


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def list_all(request, id_ugroup, tab):
    return render_to_response(USERGROUP_LIST, load_list(request, dict(), id_ugroup, tab) , context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def delete_user(request, id_ugroup):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_ugroup = auth.get_clientFactory().create_usuario_grupo()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False
            
            # For each users selected to remove
            for id_user in ids:
                try:

                    # Execute in NetworkAPI
                    client_ugroup.remover(id_user, id_ugroup)

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
                messages.add_message(request, messages.SUCCESS, user_group_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))


    # Redirect to list_all action
    return redirect('user-group.list', id_ugroup, 0)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def add_form_user(request, id_ugroup):

    try:
        
        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get Group User by ID from NetworkAPI
        lists['ugroup'] = client.create_grupo_usuario().search(id_ugroup).get('group_user')

        if request.method == "POST":

            form = UserGroupForm(client.create_usuario().list_by_group_out(id_ugroup), request.POST)
            lists['form_users'] = form

            if form.is_valid():

                user_list = form.cleaned_data['users']

                try:

                    client_ugroup = client.create_usuario_grupo()

                    for id_user in user_list:
                        client_ugroup.inserir(id_user, id_ugroup)    

                    messages.add_message(request, messages.SUCCESS, user_group_messages.get("success_insert"))

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
            else:
                lists['open_form'] = str(True)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists = load_list(request, lists,  id_ugroup, '0')

    return render_to_response(USERGROUP_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def delete_perm(request, id_ugroup):

    if request.method == 'POST':

        form = DeleteFormAux(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_perm = auth.get_clientFactory().create_permissao_administrativa()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids_aux'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each perms selected to remove
            for id_perm in ids:
                try:

                    # Execute in NetworkAPI
                    client_perm.remover(id_perm)

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
                messages.add_message(request, messages.SUCCESS, perm_group_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))


    # Redirect to list_all action
    return redirect('user-group.list', id_ugroup, 1)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def add_form_perm(request, id_ugroup):

    try:

        lists = dict()

        # Get user
        auth = AuthSession(request.session)
        client_perm = auth.get_clientFactory().create_permissao_administrativa()

        # Get Group User by ID from NetworkAPI
        lists['ugroup'] = auth.get_clientFactory().create_grupo_usuario().search(id_ugroup).get('group_user')

        if request.method == "POST":

            form = PermissionGroupForm(request.POST)
            lists['form_perms'] = form

            if form.is_valid():

                function = form.cleaned_data['function']
                read = convert_boolean_to_int(form.cleaned_data['read'])
                write = convert_boolean_to_int(form.cleaned_data['write'])

                client_perm.inserir(function, read, write, id_ugroup)    

                messages.add_message(request, messages.SUCCESS, perm_group_messages.get("success_insert"))

                return redirect('user-group.list', id_ugroup, 1)

    except PermissaoAdministrativaDuplicadaError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, perm_group_messages.get("invalid_function_duplicate") % function )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    lists['open_form'] = str(True)
    lists = load_list(request, lists,  id_ugroup, '1')

    return render_to_response(USERGROUP_LIST, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def edit_form_perm(request, id_ugroup, id_perm):

    try:
        
        lists = dict()
        lists['action_edit_perms'] = reverse("user-group-perm.edit", args=[id_ugroup,id_perm]) 

        # Get user
        auth = AuthSession(request.session)
        client_perm = auth.get_clientFactory().create_permissao_administrativa()

        # Get Group User by ID from NetworkAPI
        lists['ugroup'] = auth.get_clientFactory().create_grupo_usuario().search(id_ugroup).get('group_user')

        perm = client_perm.search(id_perm).get("perm")

        if request.method == "POST":

            form = PermissionGroupForm(request.POST)
            lists['form_perms'] = form

            if form.is_valid():

                id_perm  = form.cleaned_data['id_group_perms']
                function = form.cleaned_data['function']
                read = convert_boolean_to_int(form.cleaned_data['read'])
                write = convert_boolean_to_int(form.cleaned_data['write'])

                client_perm.alterar(id_perm, function, read, write, id_ugroup)

                messages.add_message(request, messages.SUCCESS, perm_group_messages.get("success_edit"))

                return redirect('user-group.list', id_ugroup, 1)

        #GET
        else: 
            initial={"id_group_perms" : perm.get("id"), "function" : perm.get("funcao"), "read" : convert_string_to_boolean(perm.get("leitura")), "write" : convert_string_to_boolean(perm.get("escrita"))}
            lists['form_perms'] = PermissionGroupForm(initial=initial)

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    lists['open_form'] = str(True)
    lists = load_list(request, lists,  id_ugroup, '1')

    return render_to_response(USERGROUP_LIST, lists, context_instance=RequestContext(request))