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
from CadVlan.settings import PATH_PERMLISTS
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError, PermissaoAdministrativaDuplicadaError
import logging
import re
import codecs

logger = logging.getLogger(__name__)

def parse_cad_perms(filename):
    permtree = list()
    
    with codecs.open(filename,"r", "utf-8") as fl:
        data = fl.read()
        
        #iterate over cadvlan functions
        for permcad in re.finditer(ur'^(?P<function>[A-Z][^\n]+)\n(?P<resto>(?:\t[a-zA-Z _]+\n\t\t(?:False|True)\n\t\t(?:False|True)\n)+(?:\tapi:\n(?:\t[a-zA-Z]+\n\t[a-zA-Z0-9_\(\)]+\n(?:\t\t[a-zA-Z_]+\n\t\t(?:Leitura|Escrita)\n\t\t(?:True|False)\n\t\t(?:None|Leitura|Escrita|Update_Config)\n)*)+)*)', data, re.MULTILINE|re.UNICODE):
            permcadvlan = dict()
            permcadvlan['function'] = permcad.group('function')
            permcadvlan['perms'] = list()
            permcadvlan['api_calls'] = None
            
            resto = permcad.group('resto')
            
            #iterate over cadvlan perms
            for perms_cad in re.finditer('^\t(?P<perm>[a-zA-Z_]+)\n\t\t(?P<read>False|True)\n\t\t(?P<write>False|True)\n', resto, re.MULTILINE):
                new_perm = dict()
                new_perm['perm'] = perms_cad.group('perm')
                new_perm['read'] = perms_cad.group('read')
                new_perm['write'] = perms_cad.group('write')
                
                permcadvlan['perms'].append(new_perm)
            
            api_data = re.search('\tapi:\n((?:\t[a-zA-Z]+\n\t[a-zA-Z0-9_\(\)]+\n(?:\t\t[a-zA-Z_]+\n\t\t(?:Leitura|Escrita)\n\t\t(?:True|False)\n\t\t(?:None|Leitura|Escrita|Update_Config)\n)*)+)', resto, re.MULTILINE)
            if api_data != None:
                
                permcadvlan['api_calls'] = list()
                api_data = api_data.group(1)
                
                #iterate over api calls
                for api_call in re.finditer('\t(?P<class>[a-zA-Z0-9]+)\n\t(?P<function>[a-zA-Z0-9_\(\)]+)\n(?P<mais_resto>(?:\t\t[a-zA-Z_]+\n\t\t(?:Leitura|Escrita)\n\t\t(?:True|False)\n\t\t(?:None|Leitura|Escrita|Update_Config)\n)+)*', api_data, re.MULTILINE):
                    perm_api = dict()
                    perm_api['class'] = api_call.group('class')
                    perm_api['function'] = api_call.group('function')
                    
                    #iterate over api function perms
                    resto_perms_api = api_call.group('mais_resto')
                    if resto_perms_api is not None:
                        perm_api['perms'] = list()
                        
                        for api_new_perm in re.finditer('\t\t(?P<perm>[a-zA-Z_]+)\n\t\t(?P<type>Leitura|Escrita)\n\t\t(?P<equip>True|False)\n\t\t(?P<equip_type>None|Leitura|Escrita|Update_Config)\n', resto_perms_api, re.MULTILINE):
                            perm_api_call = dict()
                            perm_api_call['perm'] = api_new_perm.group('perm')
                            perm_api_call['type'] = api_new_perm.group('type')
                            perm_api_call['equip'] = api_new_perm.group('equip')
                            perm_api_call['equip_type'] = api_new_perm.group('equip_type')
                            
                            perm_api['perms'].append(perm_api_call)
                    
                    permcadvlan['api_calls'].append(perm_api)
            
            if permcadvlan['api_calls'] is not None:
                permcadvlan['api_calls'].sort(key=lambda call: (call['class'], call['function']))
            permtree.append(permcadvlan)
    
    permtree.sort(key=lambda perm: perm['function'])
    return permtree

def parse_api_perms(filename):
    apitree = list()
    
    with codecs.open(filename,"r", "utf-8") as fl:
        data = fl.read()
        
        #iterate over api calls
        for api_call in re.finditer('(?P<class>[a-zA-Z0-9]+)\n(?P<function>[a-zA-Z0-9_\(\)]+)\n(?P<mais_resto>(?:\t[a-zA-Z_]+\n\t(?:Leitura|Escrita)\n\t(?:True|False)\n\t(?:None|Leitura|Escrita|Update_Config)\n)+)*', data, re.MULTILINE):
            perm_api = dict()
            perm_api['class'] = api_call.group('class')
            perm_api['function'] = api_call.group('function')
            
            #iterate over api function perms
            resto_perms_api = api_call.group('mais_resto')
            if resto_perms_api is not None:
                perm_api['perms'] = list()
            
                for api_new_perm in re.finditer('\t(?P<perm>[a-zA-Z_]+)\n\t(?P<type>Leitura|Escrita)\n\t(?P<equip>True|False)\n\t(?P<equip_type>None|Leitura|Escrita|Update_Config)\n', resto_perms_api, re.MULTILINE):
                    perm_api_call = dict()
                    perm_api_call['perm'] = api_new_perm.group('perm')
                    perm_api_call['type'] = api_new_perm.group('type')
                    perm_api_call['equip'] = api_new_perm.group('equip')
                    perm_api_call['equip_type'] = api_new_perm.group('equip_type')
                    
                    perm_api['perms'].append(perm_api_call)
            
            apitree.append(perm_api)
    
    apitree.sort(key=lambda call: (call['class'], call['function']))
    return apitree

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
        lists['tab'] = '0' if tab == '0' else '1' if tab == '1' else '2'
        
        lists['action_new_users'] =  reverse("user-group.form", args=[id_ugroup])
        lists['action_new_perms'] =  reverse("user-group-perm.form", args=[id_ugroup])

        #Suggestion Administrative Permission 
        list_suggestion_perm = []
        for perm in validates_dict(client.create_permissao_administrativa().listar(), 'permissao_administrativa'):

            function = perm.get('funcao')

            if not function in list_suggestion_perm:
                list_suggestion_perm.append(function)

        lists['suggestion_perm'] = list_suggestion_perm
        
        lists['cadperms'] = parse_cad_perms(PATH_PERMLISTS+"/cadperms.txt")
        lists['apiperms'] = parse_api_perms(PATH_PERMLISTS+"/apiperms.txt")


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