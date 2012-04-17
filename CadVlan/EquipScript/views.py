# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import EQUIPMENT_SCRIPT_SEARCH_LIST,EQUIPMENT_SCRIPT_ADD_FORM
from CadVlan.settings import CACHE_TIMEOUT
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError, EquipamentoRoteiroError
from django.contrib import messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.forms import DeleteForm, SearchEquipForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, equip_script_messages
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.urlresolvers import reverse
from CadVlan.EquipScript.forms import AssociateScriptForm

logger = logging.getLogger(__name__)

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def search_list(request):
    
    try:
        
        lists = dict();
        lists['search_form'] = SearchEquipForm()
        lists['del_form'] = DeleteForm()
        
        if request.method == "GET":
            
            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all script_types from NetworkAPI
            script_list = client.create_roteiro().listar()
            
            lists['add_form'] = AssociateScriptForm(script_list)
            
            if request.GET.__contains__('equip_name'):
                lists['search_form'] = search_form = SearchEquipForm(request.GET)
                
                if search_form.is_valid():
                    
                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']
                    
                    # Get all equipment scripts from NetworkAPI
                    equip_script_list = client.create_equipamento_roteiro().list_by_equip(name_equip)
                    
                    # Set equipment id
                    equipment = equip_script_list['equipamento']
                    
                    init_map = {'equip_name': equipment['name'], 'equip_id': equipment['id']}
                    
                    # New form
                    add_form = AssociateScriptForm(script_list, initial=init_map)
                    del_form = DeleteForm(initial=init_map)
                    
                    # Send to template
                    lists['del_form'] = del_form
                    lists['add_form'] = add_form
                    lists['search_form'] = search_form
                    
                    try:
                        lists['equip_script'] = equip_script_list['equipamento_roteiro']
                    except KeyError:
                        lists['equip_script'] = []
                    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_SCRIPT_SEARCH_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_all(request):
    
    equip_nam = request.POST['equip_name']
    
    if request.method == 'POST':
        
        form = DeleteForm(request.POST)
        
        if form.is_valid():
            
            # Get user
            auth = AuthSession(request.session)
            equip_script = auth.get_clientFactory().create_equipamento_roteiro()
            
            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])
            equipment = form.cleaned_data['equip_id']
            equip_nam = form.cleaned_data['equip_name']
            
            # Control others exceptions
            have_errors = False
            
            # For each script selected to remove
            for id_es in ids:
                try:
                    
                    # Execute in NetworkAPI
                    equip_script.remover(equipment, id_es)
                    
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break
                    
            # If all has ben removed
            if have_errors == False:
                messages.add_message(request, messages.SUCCESS, equip_script_messages.get("success_remove"))
                
            else:
                messages.add_message(request, messages.WARNING, error_messages.get("can_not_remove_error"))
                
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
            
    # Redirect to list_all action
    url_param = reverse("equip.script.search.list")
    if len(equip_nam) > 2:
        url_param = url_param + "?equip_name=" + equip_nam
    return HttpResponseRedirect(url_param)

@log
@login_required
@cache_page(CACHE_TIMEOUT)
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def ajax_add_form(request):
    try:
        
        # If form was submited
        if request.method == 'POST':
            
            # Get user
            auth = AuthSession(request.session)
            client = auth.get_clientFactory()
            
            # Get all script_types from NetworkAPI
            script_list = client.create_roteiro().listar()
            form = AssociateScriptForm(script_list, request.POST)
            
            if form.is_valid():
                
                # Data
                id_script = form.cleaned_data['script']
                equipment = form.cleaned_data['equip_id']
                equip_nam = form.cleaned_data['equip_name']
                
                try:
                    # Business
                    client.create_equipamento_roteiro().inserir(equipment, id_script)
                    messages.add_message(request, messages.SUCCESS, equip_script_messages.get("success_insert"))
                except EquipamentoRoteiroError, e:
                    messages.add_message(request, messages.ERROR, equip_script_messages.get("error_equal_ass"))
                    
                # Redirect to list_all action
                url_param = reverse("equip.script.search.list")
                url_param = url_param + "?equip_name=" + equip_nam
                
                response = HttpResponseRedirect(url_param)
                
                if request.is_ajax():
                    response.status_code = 278
                    
                return response
            
            else:
                # Invalid form, show errors
                return render_to_response(EQUIPMENT_SCRIPT_ADD_FORM, {'add_form': form}, context_instance=RequestContext(request))
                    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return HttpResponseServerError()