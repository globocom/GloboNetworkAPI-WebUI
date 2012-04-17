# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

import logging
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.templates import EQUIPMENT_INTERFACE_SEARCH_LIST
from CadVlan.settings import CACHE_TIMEOUT, PATCH_PANEL_ID
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from CadVlan.Auth.AuthSession import AuthSession
from networkapiclient.exception import NetworkAPIClientError
from django.contrib import messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.forms import DeleteForm, SearchEquipForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.messages import error_messages, equip_interface_messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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
            
            if request.GET.__contains__('equip_name'):
                lists['search_form'] = search_form = SearchEquipForm(request.GET)
                
                if search_form.is_valid():
                    
                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']
                    
                    # Get equipment by name from NetworkAPI
                    equipment = client.create_equipamento().listar_por_nome(name_equip)['equipamento']
                    
                    # Get all interfaces by equipment id
                    equip_interface_list = client.create_interface().list_all_by_equip(equipment['id'])
                    
                    init_map = {'equip_name': equipment['nome'], 'equip_id': equipment['id']}
                    
                    # New form
                    del_form = DeleteForm(initial=init_map)
                    
                    # Send to template
                    lists['del_form'] = del_form
                    lists['search_form'] = search_form
                    
                    if equip_interface_list.has_key('interfaces'):
                        lists['equip_interface'] = equip_interface_list['interfaces']
                    if equipment['id_tipo_equipamento'] == str(PATCH_PANEL_ID):
                        lists['pp'] = "1"
                    
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        
    return render_to_response(EQUIPMENT_INTERFACE_SEARCH_LIST, lists, context_instance=RequestContext(request))

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
            equip_interface = auth.get_clientFactory().create_interface()
            
            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])
            equip_nam = form.cleaned_data['equip_name']
            
            # Control others exceptions
            have_errors = False
            
            # For each interface selected
            for id_es in ids:
                try:
                    
                    # Remove in NetworkAPI
                    equip_interface.remover(id_es)
                    
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break
                    
            # If all has ben removed
            if have_errors == False:
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_remove"))
                
            else:
                messages.add_message(request, messages.WARNING, error_messages.get("can_not_remove_error"))
                
        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))
            
    # Redirect to list_all action
    url_param = reverse("equip.interface.search.list")
    if len(equip_nam) > 2:
        url_param = url_param + "?equip_name=" + equip_nam
    return HttpResponseRedirect(url_param)