# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
from CadVlan.Util.Decorators import log, login_required, has_perm, access_external
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from networkapiclient.exception import NomeRackDuplicadoError, RackAllreadyConfigError, RacksError, InvalidParameterError, NetworkAPIClientError, NumeroRackDuplicadoError
from django.contrib import messages
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.templates import RACK_EDIT, RACK_FORM, RACK_VIEW_AJAX
from django.template.context import RequestContext
from CadVlan.Rack.forms import RackForm
from CadVlan.Util.utility import check_regex, DataTablePaginator, validates_dict
from django.shortcuts import render_to_response, redirect
from django.template.context import Context, RequestContext
from CadVlan.messages import auth_messages, equip_messages, error_messages, rack_messages
from CadVlan.Util.converters.util import split_to_array
from CadVlan.forms import CriarVlanAmbForm, DeleteForm, ConfigForm, AplicarForm


logger = logging.getLogger(__name__)

def proximo_rack(racks):

    rack_anterior = -1
    racks = racks.get('rack')

    lists = list()
    for rack in racks:
        lists.append(int(rack.get('numero')))
    lists.sort()

    for num in lists:
        if num > rack_anterior:
            rack_anterior = rack_anterior + 1
            if not num == rack_anterior:
                return str(rack_anterior)

    rack_anterior = rack_anterior + 1
    if rack_anterior > 119:
        return ''
    return str(rack_anterior)

def validar_mac(mac):

    if not mac=='':
        if not (mac.count(':') == 5):
            raise InvalidParameterError(u'Endereco MAC invalido. Formato: FF:FF:FF:FF:FF:FF')
        mac_val = mac.split(':')
        if ((len(mac_val[0])>2) or (len(mac_val[1])>2) or (len(mac_val[2])>2) or (len(mac_val[3])>2) or (len(mac_val[4])>2) or (len(mac_val[5])>2)):
            raise InvalidParameterError(u'Endereco MAC invalido. Formato: FF:FF:FF:FF:FF:FF')

def buscar_id_equip(client, nome):
                
    id_equip = None
    if not nome=='':
            equip = client.create_equipamento().listar_por_nome(nome)
            equip = equip.get('equipamento')
            id_equip = equip['id']
            return (id_equip)
    
def buscar_nome_equip(client, rack, tipo):
    id_equip = rack.get(tipo)
    if not id_equip==None:
        equip = client.create_equipamento().listar_por_id(id_equip)
        equip = equip.get('equipamento')
        nome_eq =  equip.get('nome')
        rack[tipo] = nome_eq
    else:
        rack[tipo] = ''

def valid_rack_number(rack_number):
   if not rack_number < 120:
      raise InvalidParameterError(u'Numero de Rack invalido. Intervalo valido: 0 - 119') 

def valid_rack_name(rack_name):
   if not check_regex(rack_name, r'^[A-Z][A-Z][0-9][0-9]'):
      raise InvalidParameterError('Nome inváildo. Ex: AA00')

def get_msg(request, var, nome, operation):

    var = var.get('rack_conf')
    var = str(var)

    if var=="True":
        if operation=='CONFIG':
            msg = rack_messages.get('sucess_create_config') % nome 
        elif operation=='APLICAR':
            msg = rack_messages.get('sucess_aplicar_config') % nome
        messages.add_message(request, messages.SUCCESS, msg)
    else:
        if operation=='CONFIG':
            msg = rack_messages.get('can_not_create_all') % nome    
        elif operation=='APLICAR':
            msg = rack_messages.get('can_not_aplicar_config') % nome
        messages.add_message(request, messages.ERROR, msg)

def rack_config_delete (request, client, form, operation):

        if form.is_valid():

            if operation=='CONFIG':
                id = 'ids_config'
            elif operation == 'DELETE':
                id = 'ids'
            elif operation=='APLICAR':
                id = 'ids_aplicar'


            # All ids selected
            ids = split_to_array(form.cleaned_data[id])

            # All messages to display
            error_list = list()
            error_list_config = list()
            all_ready_msg_rack_error = False

            # Control others exceptions
            have_errors = False

            # For each rack selected
            for id_rack in ids:
                try:
                    racks = client.create_rack().list()
                    racks = racks.get('rack')
                    for ra in racks:
                        if ra.get('id')==id_rack:
                            rack = ra
                    nome = rack.get('nome')
                    if operation == 'DELETE':
                        msg_sucess = "success_remove"
                        client.create_rack().remover(id_rack)
                    elif operation == 'CONFIG':
                        var = client.create_rack().gerar_arq_config(id_rack)
                        var = var.get('sucesso')
                        get_msg(request, var, nome, operation)
                    elif operation=='APLICAR':
                        var = client.create_rack().aplicar_configuracao(id_rack)
                        var = var.get('sucesso')
                        get_msg(request, var, nome, operation)
                except RackAllreadyConfigError, e:
                    logger.error(e)
                    error_list_config.append(id_rack)
                except RacksError, e:
                    logger.error(e)
                    if not all_ready_msg_rack_error:
                        messages.add_message(request, messages.ERROR, e)
                    all_ready_msg_rack_error = True
                    error_list.append(id_rack)
                except NetworkAPIClientError, e:
                    logger.error(e)
                    messages.add_message(request, messages.ERROR, e)
                    have_errors = True
                    break

            if len(error_list_config) > 0:

                msg = ""
                for id_error in error_list_config:
                    msg = msg + id_error + ','

                messages.add_message(request, messages.WARNING, msg)
                have_errors = True

            if len(error_list) == len(ids):
                messages.add_message(
                    request, messages.ERROR, error_messages.get("can_not_remove_all"))

            elif len(error_list) > 0:
                msg = ""
                for id_error in error_list:
                    msg = msg + id_error + ", "

                msg = error_messages.get("can_not_remove") % msg[:-2]

                messages.add_message(request, messages.WARNING, msg)

            elif (not operation=='CONFIG') and (not operation=='APLICAR') and (have_errors == False):
                messages.add_message(
                    request, messages.SUCCESS, rack_messages.get(msg_sucess))

            return redirect("ajax.view.rack")

        else:
            messages.add_message(request, messages.ERROR, error_messages.get("select_one"))

         # Redirect to list_all action
        return redirect("ajax.view.rack")

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
def rack_form(request):
   
    try:

        lists = dict()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = RackForm()

        if request.method == 'GET':

            racks = client.create_rack().list()
            numero = proximo_rack(racks)
            form = RackForm(initial={'rack_number': numero})

        if request.method == 'POST':

            form = RackForm(request.POST)
            if form.is_valid():
                rack_number = form.cleaned_data['rack_number']
                rack_name = form.cleaned_data['rack_name']
                mac_sw1 = form.cleaned_data['mac_address_sw1']
                mac_sw2 = form.cleaned_data['mac_address_sw2']
                mac_ilo = form.cleaned_data['mac_address_ilo']
                nome_sw1 = form.cleaned_data['nome_sw1']
                nome_sw2 = form.cleaned_data['nome_sw2']
                nome_ilo = form.cleaned_data['nome_ilo']

                # validacao: Numero do Rack
                valid_rack_number(rack_number)
 
                # validacao: Nome do Rack
                valid_rack_name(rack_name)

                # Validacao: MAC 
                validar_mac(mac_sw1)
                validar_mac(mac_sw2)
                validar_mac(mac_ilo)
                
                id_sw1 = buscar_id_equip(client,nome_sw1)
                id_sw2 = buscar_id_equip(client,nome_sw2)
                id_ilo = buscar_id_equip(client,nome_ilo)
 
                rack = client.create_rack().insert_rack(rack_number, rack_name, mac_sw1, mac_sw2, mac_ilo, id_sw1, id_sw2, id_ilo)
                messages.add_message(request, messages.SUCCESS, rack_messages.get("success_insert"))

                form = RackForm()
                return redirect('ajax.view.rack')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(RACK_FORM, {'form': form}, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}, {"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def ajax_view(request):

    # Get user
    auth = AuthSession(request.session)
    client_api = auth.get_clientFactory()

    return ajax_rack_view(request, client_api)

def ajax_rack_view(request, client_api):

    try:

        racks = dict()

        # Get all racks from NetworkAPI
        racks = client_api.create_rack().list()

        if not racks.has_key("rack"):
                    racks["rack"] = []

        rack = racks.get('rack')

        for var in rack:
            mac_1 = var.get("mac_sw1")           
            mac_2 = var.get("mac_sw2")           
            mac_3 = var.get("mac_ilo")
           
            buscar_nome_equip(client_api, var, 'id_sw1')
            buscar_nome_equip(client_api, var, 'id_sw2')
            buscar_nome_equip(client_api, var, 'id_ilo')

            if mac_1==None:
                var['mac_sw1'] = ''
            if mac_2==None:
                var['mac_sw2'] = ''
            if mac_3==None:
                var['mac_ilo'] = ''

            var['config'] = var.get("config")

            if var.get("rack_vlan_amb")=='True':
                var['rack_vlan_amb'] = "True"
            else:
                var['rack_vlan_amb'] = "False"

        racks['delete_form'] = DeleteForm()
        racks['config_form'] = ConfigForm()
        racks['aplicar_form'] = AplicarForm()
        racks['criar_vlan_amb_form'] = CriarVlanAmbForm()


    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(RACK_VIEW_AJAX, racks, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
def rack_edit(request, id_rack):

    lists = dict()
    lists['id'] = id_rack

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        # Get all racks from NetworkAPI
        racks = client.create_rack().list()

        if not racks.has_key("rack"):
                    racks["rack"] = []

        rackn = racks.get('rack')
        for var in rackn:
            if (var['id']==id_rack):
                rack = var

        if request.method == 'GET':

            nome_eq1 = buscar_nome_equip(client, rack, 'id_sw1')
            nome_eq2 = buscar_nome_equip(client, rack, 'id_sw2')
            nome_eq3 = buscar_nome_equip(client, rack, 'id_ilo')
            lists['numero'] = rack.get('numero')

            lists['form'] = RackForm(initial={'rack_number': rack.get('numero'), 'rack_name': rack.get('nome'), "mac_address_sw1": rack.get('mac_sw1'), "mac_address_sw2": rack.get("mac_sw2"), "mac_address_ilo": rack.get('mac_ilo'), "nome_sw1": rack.get('id_sw1'), "nome_sw2": rack.get('id_sw2'), "nome_ilo": rack.get('id_ilo')})
    
        if request.method == 'POST':
            form = RackForm(request.POST)
            lists['form'] = form

            if form.is_valid():
                numero = form.cleaned_data['rack_number']
                nome = form.cleaned_data['rack_name']
                mac_sw1 = form.cleaned_data['mac_address_sw1']
                mac_sw2 = form.cleaned_data['mac_address_sw2']
                mac_ilo = form.cleaned_data['mac_address_ilo']
                nome_sw1 = form.cleaned_data['nome_sw1']
                nome_sw2 = form.cleaned_data['nome_sw2']
                nome_ilo = form.cleaned_data['nome_ilo']

                # Validacao: MAC 
                validar_mac(mac_sw1)
                validar_mac(mac_sw2)
                validar_mac(mac_ilo)

                id_sw1 = buscar_id_equip(client,nome_sw1)
                id_sw2 = buscar_id_equip(client,nome_sw2)
                id_ilo = buscar_id_equip(client,nome_ilo)

                rack = client.create_rack().edit_rack(id_rack, numero, nome, mac_sw1, mac_sw2, mac_ilo, id_sw1, id_sw2, id_ilo)
                messages.add_message(request, messages.SUCCESS, rack_messages.get("success_edit"))

                return redirect('ajax.view.rack')

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(RACK_EDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_config (request):

    if request.method == 'POST':

        form = ConfigForm(request.POST)
       
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete (request, client, form, 'CONFIG')

    return redirect("ajax.view.rack")


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_delete (request):

    if request.method == 'POST':
        
        form = DeleteForm(request.POST)

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete (request, client, form, 'DELETE')

    return redirect("ajax.view.rack")


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_aplicar_config(request):

    if request.method == 'POST':

        form = AplicarForm(request.POST)

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete (request, client, form, 'APLICAR')

    return redirect("ajax.view.rack")

