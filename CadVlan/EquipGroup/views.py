# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.EquipGroup.forms import EquipGroupForm, UserEquipGroupForm
from CadVlan.Equipment.business import cache_list_equipment_all
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.utility import convert_boolean_to_int, convert_int_to_boolean, validates_dict
from CadVlan.forms import DeleteForm, DeleteFormAux
from CadVlan.messages import error_messages, equip_group_messages
from CadVlan.permissions import ADMINISTRATION
from CadVlan.templates import EQUIPMENT_GROUP_LIST, EQUIPMENT_GROUP_FORM
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from networkapiclient.exception import NetworkAPIClientError, EquipmentDontRemoveError, DireitoGrupoEquipamentoDuplicadoError
import logging

logger = logging.getLogger(__name__)


def load_list(request,lists,id_egroup,tab):
    
    try:
        
        equipament_list = lists

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        equipament_list['equipments'] = validates_dict(client.create_equipamento().list_by_group(id_egroup), 'equipments')
        equipament_list['form'] = DeleteForm()
        equipament_list['egroup'] = client.create_grupo_equipamento().search(id_egroup)['group_equipament']
        equipament_list['tab'] = '0' if tab == '0' else '1'
        
        group_equipment_perm = client.create_direito_grupo_equipamento().listar_por_grupo_equipamento(id_egroup).get("direito_grupo_equipamento")
        equipament_list['ugroups'] = group_equipment_perm
        equipament_list['form_ugroup'] = DeleteFormAux()
        
        if not 'ugroup_form' in equipament_list:
            ugroups = client.create_grupo_usuario().listar()
            egroup = client.create_grupo_equipamento().search(id_egroup)['group_equipament']
            equipament_list['ugroup_form'] = UserEquipGroupForm(ugroups,initial={"id_egroup":id_egroup,"egroup":egroup.get('nome')})
            
        if not 'url_form' in equipament_list:
            lists['url_form'] = reverse("equip-user-group.form",args=[id_egroup])
            
        if not 'open_form' in equipament_list:
            lists['open_form'] = 'False'
            
        if not 'url_edit' in equipament_list:
            lists['edit'] = 'False'
        else:
            lists['edit'] = 'True'

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return equipament_list
    

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def list_all(request, id_egroup, tab):
    return render_to_response(EQUIPMENT_GROUP_LIST, load_list(request, dict(), id_egroup, tab) , context_instance=RequestContext(request))



@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
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
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
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

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def add_right(request, id_egroup):
   
    lists = dict()
    lists['id_egroup'] = id_egroup
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        user_group = client.create_grupo_usuario().listar()
        
        
        if request.method == 'POST':
            
            form = UserEquipGroupForm(user_group,request.POST)
            lists['ugroup_form'] = form
            
            if form.is_valid():
               
                id_ugroup = form.cleaned_data['ugroup']
                id_egroup = form.cleaned_data['id_egroup']
                update =  convert_boolean_to_int(form.cleaned_data['update'])
                delete = convert_boolean_to_int(form.cleaned_data['delete'])
                read = convert_boolean_to_int(form.cleaned_data['read'])
                write =  convert_boolean_to_int(form.cleaned_data['write'])
                
                client.create_direito_grupo_equipamento().inserir(id_ugroup, id_egroup, read, write, update, delete)
                messages.add_message(request, messages.SUCCESS, equip_group_messages.get("sucess_group_user_equip"))
                # Redirect to list_all action
                return redirect('equip-group.list', id_egroup, 1)
            else:
                lists['open_form'] = "True"
    
    except DireitoGrupoEquipamentoDuplicadoError, e:
        logger.error(e)
        lists['open_form'] = "True"
        messages.add_message(request, messages.ERROR, equip_group_messages.get("duplicated_error"))
    except NetworkAPIClientError, e:
        logger.error(e)
        lists['open_form'] = "True"
        messages.add_message(request, messages.ERROR, e)
    
        
    
    lists['url_form'] = reverse("equip-user-group.form",args=[id_egroup])
    lists = load_list(request, lists, id_egroup, 1)
    
    return render_to_response(EQUIPMENT_GROUP_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def edit_right(request, id_egroup, id_right):
   
    lists = dict()
    lists['id_egroup'] = id_egroup
    
    try:
        
        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        
        user_group = client.create_grupo_usuario().listar()
        
        
        if request.method == 'POST':
            
            form = UserEquipGroupForm(user_group,request.POST)
            lists['ugroup_form'] = form
            
            if form.is_valid():
                
                update =  convert_boolean_to_int(form.cleaned_data['update'])
                delete = convert_boolean_to_int(form.cleaned_data['delete'])
                read = convert_boolean_to_int(form.cleaned_data['read'])
                write =  convert_boolean_to_int(form.cleaned_data['write'])
                
                client.create_direito_grupo_equipamento().alterar(id_right, read, write, update, delete)
                messages.add_message(request, messages.SUCCESS, equip_group_messages.get("sucess_group_user_equip_edit"))
                # Redirect to list_all action
                return redirect('equip-group.list', id_egroup, 1)
            else:
                lists['open_form'] = "True"
        
        #Get Requisition    
        else:
            
            # Get Group Equipament by ID from NetworkAPI
            egroup = client.create_grupo_equipamento().search(id_egroup)['group_equipament']
            
            right = client.create_direito_grupo_equipamento().buscar_por_id(id_right).get('direito_grupo_equipamento')
            write = convert_int_to_boolean(right.get('escrita'))
            update = convert_int_to_boolean(right.get('alterar_config'))
            read = convert_int_to_boolean(right.get('leitura'))
            delete = convert_int_to_boolean(right.get('exclusao'))
            
            lists['ugroup_form'] = UserEquipGroupForm(user_group,initial={"id_egroup":id_egroup,
                                                                          "egroup":egroup.get('nome'),
                                                                          "delete":delete,
                                                                          "update":update,
                                                                          "write": write,
                                                                          "read":read,
                                                                          'ugroup':right.get("id_grupo_usuario")})
            
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    
    lists['url_edit'] = reverse("equip-user-group.edit",args=[id_egroup,id_right])
    lists = load_list(request, lists, id_egroup, 1)
    lists['open_form'] = 'True'
    
    return render_to_response(EQUIPMENT_GROUP_LIST, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": ADMINISTRATION, "read": True},{"permission": ADMINISTRATION, "write": True}])
def delete_right(request, id_egroup):
    if request.method == 'POST':

        form = DeleteFormAux(request.POST)

        if form.is_valid():

            # Get user
            auth = AuthSession(request.session)
            client_equipament = auth.get_clientFactory().create_direito_grupo_equipamento()

            # All ids to be deleted
            ids = split_to_array(form.cleaned_data['ids_aux'])

            # All messages to display
            error_list = list()

            # Control others exceptions
            have_errors = False

            # For each script selected to remove
            for id_right in ids:
                try:

                    # Execute in NetworkAPI
                    client_equipament.remover(id_right)

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
                messages.add_message(request, messages.SUCCESS, equip_group_messages.get("sucesso_user_equip_remove"))

            else:
                messages.add_message(request, messages.SUCCESS, error_messages.get("can_not_remove_error"))

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

    # Redirect to list_all action
    return redirect('equip-group.list', id_egroup, 1)