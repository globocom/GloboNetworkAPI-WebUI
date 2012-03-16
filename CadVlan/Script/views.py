# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Auth.Decorators import log, login_required, has_perm
from CadVlan.templates import SCRIPT_LIST, SCRIPT_FORM
from CadVlan.settings import CACHE_TIMEOUT
from django.shortcuts import render_to_response, redirect
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, RoteiroError, NomeRoteiroDuplicadoError
from django.contrib import messages
from CadVlan.messages import error_messages, script_messages
from CadVlan.Util.converters.util import split_to_array, replace_id_to_name
from CadVlan.permissions import SCRIPT_MANAGEMENT
from CadVlan.forms import DeleteForm
from CadVlan.Script.forms import ScriptForm
from django.template.defaultfilters import upper

logger = logging.getLogger(__name__)

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm(SCRIPT_MANAGEMENT, read = True)
def list_all(request):
    
    try:
        
        lists = dict();
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get all scripts from NetworkAPI
        script_list = client.create_roteiro().listar()
        # Get all script_types from NetworkAPI
        script_type_list = client.create_tipo_roteiro().listar()
        
        # Business
        lists['roteiro'] = replace_id_to_name(script_list["roteiro"], script_type_list["tipo_roteiro"], "id_tipo_roteiro", "id", "tipo")
        lists['form'] = DeleteForm()
        
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(SCRIPT_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm(SCRIPT_MANAGEMENT, write = True)
def delete_all(request):
    
    if request.method == 'POST':
        
        form = DeleteForm(request.POST)
        
        if form.is_valid():
            
            # Get user
            auth = AuthSession(request.session)
            roteiro = auth.get_clientFactory().create_roteiro()
            
            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])
            
            # All messages to display
            error_list = list()
            
            # Control others exceptions
            have_errors = False
            
            # For each script selected to remove
            for id_script in ids:
                try:
                    
                    # Execute in NetworkAPI
                    roteiro.remover(id_script)
                    
                except RoteiroError, e:
                    # If isnt possible, add in error list
                    error_list.append(id_script)
                    
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
                messages.add_message(request, messages.SUCCESS, script_messages.get("success_remove"))
        
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
            
    # Redirect to list_all action
    return redirect("script.list")

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm(SCRIPT_MANAGEMENT, write = True, read = True)
def add_form(request):
    
    try:
        
        # If form was submited
        if request.method == 'POST':
            
            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all script_types from NetworkAPI
            script_type_list = client.create_tipo_roteiro().listar()
            form = ScriptForm(script_type_list, request.POST)
            
            if form.is_valid():
                
                # Data
                name = upper(form.cleaned_data['name'])
                script_type = form.cleaned_data['script_type']
                description = form.cleaned_data['description']
                
                try:
                    # Business
                    client.create_roteiro().inserir(script_type, name, description)
                    messages.add_message(request, messages.SUCCESS, script_messages.get("success_insert"))
                    
                    return redirect('script.list')
                except NomeRoteiroDuplicadoError, e:
                    messages.add_message(request, messages.ERROR, script_messages.get("error_equal_name") % name)
                    
        else:
            
            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all script_types from NetworkAPI
            script_type_list = client.create_tipo_roteiro().listar()
            
            # New form
            form = ScriptForm(script_type_list)
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    return render_to_response(SCRIPT_FORM, {'form': form}, context_instance=RequestContext(request))