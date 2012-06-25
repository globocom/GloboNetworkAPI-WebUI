# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.EquipGroup.forms import EquipGroupForm
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.forms import DeleteForm, DeleteFormAux
from CadVlan.messages import error_messages, equip_group_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import EQUIPMENT_GROUP_LIST, EQUIPMENT_GROUP_FORM
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError, EquipmentDontRemoveError
import logging
from CadVlan.Equipment.business import cache_list_equipment_all

logger = logging.getLogger(__name__)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True}])
def list_all(request, id_egroup, tab):

    try:

        equipament_list = dict()

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        list_equip = client.create_equipamento().list_by_group(id_egroup)
        if list_equip is not None:
            if type(list_equip.get('equipments')) == dict:
                equipament_list['equipments'] = [list_equip.get('equipments')]
            else:
                equipament_list['equipments'] = list_equip.get('equipments')
         
        equipament_list['form'] = DeleteForm()
        equipament_list['egroup'] = client.create_grupo_equipamento().search(id_egroup)['group_equipament']
        equipament_list['tab'] = '0' if tab == '0' else '1'
        
        group_equipment_perm = client.create_direito_grupo_equipamento().listar_por_grupo_equipamento(id_egroup).get("direito_grupo_equipamento")
        equipament_list['ugroups'] = group_equipment_perm
        equipament_list['form_ugroup'] = DeleteFormAux()

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_GROUP_LIST, equipament_list, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def delete_all(request, id_egroup):

    if request.method == 'POST':

        form = DeleteForm(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_equipament = auth.get_clientFactory().create_equipamento()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_equip in ids:
                try:

                    # Execute in NetworkAPI
                    client_equipament.remover_grupo(id_equip, id_egroup)
                    
                except EquipmentDontRemoveError, e:
                    # If isnt possible, add in error list
                    error_list.append(id_equip)

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            # If cant remove someones
            if len(error_list) > 0:
                
                list_equipment = cache_list_equipment_all(client_equipament)
                
                msg = ""
                for id_error in error_list:
                    
                    for equip in list_equipment:
                        
                        if equip['id'] == id_error:
                            msg = msg + equip['nome'] + ", "
                            break

                msg = equip_group_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            # If all has ben removed
            elif have_errors == False:
                messages.add_message(request, messages.SUCCESS, equip_group_messages.get("success_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('equip-group.list', id_egroup, 0)

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "write": True}])
def add_form(request, id_egroup):

    try:
        
        form = EquipGroupForm()
        equipment = None        
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        # Get Group Equipament by ID from NetworkAPI
        egroup = client.create_grupo_equipamento().search(id_egroup)['group_equipament']

        if request.method == "POST":

            form = EquipGroupForm(request.POST)

            if form.is_valid():
                id_egroup = form.cleaned_data['id_egroup']
                equip_name = form.cleaned_data['equip_name']
                
                client_equip = client.create_equipamento()
                
                # Get equipment by name from NetworkAPI
                equipment = client_equip.listar_por_nome(equip_name)['equipamento']

                try:
                    client_equip.associar_grupo(equipment['id'], id_egroup)
                    messages.add_message(request, messages.SUCCESS, equip_group_messages.get("success_insert"))
                    form = EquipGroupForm(initial={'id_egroup':  egroup['id'], 'egroup':  egroup['nome'] })

                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)

        else:
            
            form = EquipGroupForm(initial={'id_egroup':  egroup['id'], 'egroup':  egroup['nome'] })

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(EQUIPMENT_GROUP_FORM, {'form': form,'id_egroup':id_egroup}, context_instance=RequestContext(request))