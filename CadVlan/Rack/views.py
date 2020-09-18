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

import json
import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_protect

from CadVlan import templates
from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.forms import CriarVlanAmbForm, DeleteForm, ConfigForm, AplicarForm, AlocarForm
from CadVlan.messages import error_messages, rack_messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.Rack.forms import RackForm
from CadVlan.Util.converters.util import split_to_array
from CadVlan.Util.Decorators import log, login_required, has_perm
from CadVlan.Util.utility import check_regex

from networkapiclient.exception import RackAllreadyConfigError, RacksError
from networkapiclient.exception import InvalidParameterError, NetworkAPIClientError


logger = logging.getLogger(__name__)


def proximo_rack(racks, qtd_rack=119):

    if len(racks)==qtd_rack:
        return -1

    rack_anterior = -1
    racks_ids = list()

    for rack in racks:
        racks_ids.append(int(rack.get('numero')))
    racks_ids.sort()

    for num in racks_ids:
        if num > rack_anterior:
            rack_anterior = rack_anterior + 1
            if not num == rack_anterior:
                return str(rack_anterior)

    return str(rack_anterior+1)

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


def valid_rack_number_dc(rack_number, racks):
   if not int(rack_number) < int(racks):
      raise InvalidParameterError(u'Numero de Rack invalido. Intervalo valido: 0 - %s' % str(racks))


def valid_rack_name(rack_name):
   if not check_regex(rack_name, r'^[A-Z][A-Z][0-9][0-9]'):
      raise InvalidParameterError('Nome inválido. Ex: AA00')


def get_msg(request, var, nome, operation):

    var = var.get('rack_conf')
    var = str(var)
    msg = ""

    if var=="True":
        if operation=='CONFIG':
            msg = rack_messages.get('sucess_create_config') % nome
        elif operation=='ALOCAR':
            msg = rack_messages.get('sucess_alocar_config') % nome
        elif operation=='APLICAR':
            msg = rack_messages.get('sucess_aplicar_config') % nome
        messages.add_message(request, messages.SUCCESS, msg)
    else:
        if operation=='CONFIG':
            msg = rack_messages.get('can_not_create_all') % nome    
        elif operation=='ALOCAR':
            msg = rack_messages.get('can_not_alocar_config') % nome
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
            elif operation=='ALOCAR':
                id = 'ids_alocar'

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
                        var = client.create_apirack().rack_deploy(id_rack)
                        var = var.get('sucesso')
                        get_msg(request, var, nome, 'APLICAR')
                    elif operation=='ALOCAR':
                        var = client.create_rack().alocar_configuracao(id_rack)
                        var = var.get('sucesso')
                        get_msg(request, var, nome, operation)
                except RackAllreadyConfigError as e:
                    logger.error(e)
                    error_list_config.append(id_rack)
                except RacksError as e:
                    logger.error(e)
                    if not all_ready_msg_rack_error:
                        messages.add_message(request, messages.ERROR, e)
                    all_ready_msg_rack_error = True
                    error_list.append(id_rack)
                except NetworkAPIClientError as e:
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

            elif (not operation=='CONFIG') and (not operation=='ALOCAR') and (not operation=='APLICAR') and (have_errors == False):
                messages.add_message(request, messages.SUCCESS, rack_messages.get(msg_sucess))

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
            numero = proximo_rack(racks.get("rack"))
            form = RackForm(initial={'rack_number': numero})

        if request.method == 'POST':

            form = RackForm(request.POST)
            rack = dict()
            if form.is_valid():
                rack['numero'] = form.cleaned_data['rack_number']
                rack['nome'] = form.cleaned_data['rack_name']
                rack['mac_sw1'] = form.cleaned_data['mac_address_sw1']
                rack['mac_sw2'] = form.cleaned_data['mac_address_sw2']
                rack['mac_ilo'] = form.cleaned_data['mac_address_ilo']
                nome_sw1 = form.cleaned_data['nome_sw1']
                nome_sw2 = form.cleaned_data['nome_sw2']
                nome_ilo = form.cleaned_data['nome_ilo']

                # validacao: Numero do Rack
                valid_rack_number(rack['numero'])
 
                # validacao: Nome do Rack
                valid_rack_name(rack['nome'])

                # Validacao: MAC 
                validar_mac(rack['mac_sw1'])
                validar_mac(rack['mac_sw2'])
                validar_mac(rack['mac_ilo'])
                
                rack['id_sw1'] = buscar_id_equip(client,nome_sw1)
                rack['id_sw2'] = buscar_id_equip(client,nome_sw2)
                rack['id_ilo'] = buscar_id_equip(client,nome_ilo)
 
                rack = client.create_apirack().insert_rack(rack)
                messages.add_message(request, messages.SUCCESS, rack_messages.get("success_insert"))

                form = RackForm()
                return redirect('ajax.view.rack')

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(templates.RACK_FORM, {'form': form}, context_instance=RequestContext(request))


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
        racks['alocar_form'] = AlocarForm()


    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(templates.RACK_VIEW_AJAX, racks, context_instance=RequestContext(request))


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
            try:
                rack_num = rack.get('numero')
                rack_name = rack.get('nome')
            except:
                rack_num = None
                pass
            lists['numero'] = rack_num
            try:
                nome_sw1 = client.create_equipamento().listar_por_id(rack.get('id_sw1'))['equipamento']['nome']
                mac_sw1 = rack.get('mac_sw1')
            except:
                nome_sw1 = None
                mac_sw1 = None
                pass
            try:
                nome_sw2 = client.create_equipamento().listar_por_id(rack.get('id_sw2'))['equipamento']['nome']
                mac_sw2 = rack.get("mac_sw2")
            except:
                nome_sw2 = None
                mac_sw2 = None
                pass
            try:
                nome_ilo = client.create_equipamento().listar_por_id(rack.get('id_ilo'))['equipamento']['nome']
                mac_ilo = rack.get('mac_ilo')
            except:
                nome_ilo = None
                mac_ilo = None
                pass
            lists['form'] = RackForm(initial={'rack_number': rack_num, 'rack_name': rack_name, "nome_sw1": nome_sw1,
                                              'mac_address_sw1': mac_sw1, 'mac_address_sw2': mac_sw2, 'nome_sw2': nome_sw2,
                                              'mac_address_ilo': mac_ilo, 'nome_ilo': nome_ilo})
    
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

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(templates.RACK_EDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_config (request):

    if request.method == 'POST':

        form = ConfigForm(request.POST)
       
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete(request, client, form, 'CONFIG')

    return redirect("ajax.view.rack")


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_delete (request):

    if request.method == 'POST':
        
        form = DeleteForm(request.POST)

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete(request, client, form, 'DELETE')

    return redirect("ajax.view.rack")


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_alocar(request):

    if request.method == 'POST':

        form = AlocarForm(request.POST)

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete(request, client, form, 'ALOCAR')

    return redirect("ajax.view.rack")


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def rack_deploy(request):

    if request.method == 'POST':

        form = AplicarForm(request.POST)

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        rack_config_delete(request, client, form, 'APLICAR')

    return redirect("ajax.view.rack")


# ################################################################################   DC

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
def newrack(request, fabric_id):

    try:

        lists = dict()
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        form = RackForm()
        lists = dict()
        lists["fabric_id"] = fabric_id
        lists["action"] = reverse('rack.add', args=[fabric_id])

        fabric = client.create_apirack().get_fabric(fabric_id=fabric_id).get("fabric")[0]
        fabric_racks = fabric.get("racks")

        if request.method == 'GET':
            racks = client.create_apirack().get_rack(fabric_id=fabric_id)
            numero = proximo_rack(racks.get("racks"), fabric_racks)
            if numero < 0:
                messages.add_message(request, messages.ERROR, "Fabric já possui %s racks." % str(fabric_racks))
                return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))
            form = RackForm(initial={'rack_number': numero})

        lists["form"] = form

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

                #valid_rack_name(rack_name)

                validar_mac(mac_sw1)
                validar_mac(mac_sw2)
                validar_mac(mac_ilo)

                id_sw1 = buscar_id_equip(client,nome_sw1)
                id_sw2 = buscar_id_equip(client,nome_sw2)
                id_ilo = buscar_id_equip(client,nome_ilo)

                rack = {
                    'number': rack_number,
                    'name': rack_name,
                    'id_sw1': id_sw1,
                    'mac_sw1': mac_sw1,
                    'id_sw2': id_sw2,
                    'mac_sw2': mac_sw2,
                    'id_ilo': id_ilo,
                    'mac_ilo': mac_ilo,
                    'fabric_id': fabric_id
                }

                rack = client.create_apirack().newrack(rack)
                messages.add_message(request, messages.SUCCESS, rack_messages.get("success_insert"))

                return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return HttpResponseRedirect(reverse('rack.add', args=[fabric_id]))

    return render_to_response(templates.RACK_DC_ADD, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
def put_rack(request, rack_id, fabric_id):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists['id'] = rack_id
        lists["fabric_id"] = fabric_id
        lists["action"] = reverse('rack.new.edit', args=[rack_id, fabric_id])


        racks = client.create_apirack().get_rack(rack_id=rack_id)

        rack = racks.get("racks")[0] if racks.get("racks") else dict()

        lists['numero'] = rack.get("numero")

        lists['form'] = RackForm(initial={'rack_number': rack.get("numero"),
                                          'rack_name': rack.get("nome"),
                                          "nome_sw1": rack.get("id_sw1"),
                                          'nome_sw2': rack.get("id_sw2"),
                                          'nome_ilo': rack.get("id_ilo"),
                                          'mac_address_sw1': rack.get("mac_sw1"),
                                          'mac_address_sw2': rack.get("mac_sw2"),
                                          'mac_address_ilo': rack.get("mac_ilo")})

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

                id_sw1 = buscar_id_equip(client, nome_sw1)
                id_sw2 = buscar_id_equip(client, nome_sw2)
                id_ilo = buscar_id_equip(client, nome_ilo)

                rack = {
                    'id': rack_id,
                    'number': numero,
                    'name': nome,
                    'id_sw1': id_sw1,
                    'mac_sw1': mac_sw1,
                    'id_sw2': id_sw2,
                    'mac_sw2': mac_sw2,
                    'id_ilo': id_ilo,
                    'mac_ilo': mac_ilo,
                    'fabric_id': fabric_id
                }
                rack = client.create_apirack().put_rack(rack_id, rack)
                messages.add_message(request, messages.SUCCESS, "Rack foi editado.")

                return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(templates.RACK_NEWEDIT, lists, context_instance=RequestContext(request))

    return render_to_response(templates.RACK_NEWEDIT, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def remove_rack(request, fabric_id, rack_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    try:
        client.create_apirack().delete_rack(rack_id)
        messages.add_message(request, messages.SUCCESS, rack_messages.get("success_remove"))
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Não foi possivel remover o rack. Erro: %s" % e)
    finally:
        return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def remove_rack_env(request, fabric_id, rack_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    try:
        client.create_apirack().remove_rack_environments(rack_id)
        messages.add_message(request, messages.SUCCESS, "Os ambientes e vlans do rack foram removidos.")
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Não foi possivel remover os ambientes e vlans do rack. "
                                                      "Erro: %s" % e)
    finally:
        return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def vlans_rack (request, fabric_id, rack_id):

    try:
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()
        client.create_apirack().rackenvironments(rack_id)
        messages.add_message(request, messages.SUCCESS, rack_messages.get("sucess_alocar_config"))
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Os ambientes do rack não foram alocados. Erro: %s" % e)

    return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def files_rack (request, fabric_id, rack_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    try:
        client.create_apirack().rackfiles(rack_id)
        messages.add_message(request, messages.SUCCESS, rack_messages.get("sucess_create_config"))
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Os arquivos de configuração não foram gerados. Erro: %s" % e)

    return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def deploy_rack_new (request, fabric_id, rack_id):


    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    try:
        client.create_apirack().rack_deploy(rack_id)
        messages.add_message(request, messages.SUCCESS, rack_messages.get("sucess_aplicar_config"))
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Erro ao deployar. Erro: %s" % e)

    return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))


@log
@login_required
@csrf_protect
def datacenter(request):

    try:
        lists = dict()

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        dc = client.create_apirack().list()
        dc_list = dc.get("dc")

        lists["dc"] = dc_list

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    return render_to_response(templates.LISTDC, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
@csrf_protect
def new_datacenter(request):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        if request.method == 'POST':

            dc = dict()
            dc['dcname'] = request.POST.get('name')
            dc['address'] = request.POST.get('address')

            newdc = client.create_apirack().save_dc(dc)
            id = newdc.get('dc').get('id')

            return HttpResponseRedirect(reverse('fabric.cadastro', args=[id]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, "Datacenter não foi cadastrado. Erro: %s" % e)
    return render_to_response(templates.DC_FORM, {'form': {}}, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def remove_datacenter(request, dc_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    try:
        client.create_apirack().delete_datacenter(dc_id)
        messages.add_message(request, messages.SUCCESS, "O datacenter foi removido com sucesso.")
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Não foi possivel remover o datacenter. Erro: %s" % e)
    finally:
        return HttpResponseRedirect(reverse("listdc"))


@log
@login_required
@csrf_protect
def fabric(request, fabric_id):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        racks = client.create_apirack().get_rack(fabric_id=fabric_id)

        lists = dict()
        lists["racks"] = racks.get("racks")
        lists["fabric_id"] = fabric_id
        lists["action"] = reverse('fabric', args=[fabric_id])

        if request.method =='GET':

            fabric = client.create_apirack().get_fabric(fabric_id=fabric_id).get("fabric")[0]
            if fabric.get("config"):
                fabric["config"] = json.dumps(fabric.get("config"))
            lists["fabric"] = fabric

        if request.method == 'POST':
            fabric = dict()
            fabric['id'] = fabric_id
            fabric['name'] = request.POST.get('fabricname')
            fabric['racks'] = request.POST.get('rack')
            fabric['spines'] = request.POST.get('spn')
            fabric['leafs'] = request.POST.get('lfs')
            fabric['config'] = request.POST.get('config')

            fabric_dict = client.create_apirack().put_fabric(fabric_id, fabric)
            fabric_dict = fabric_dict.get("fabric")
            if fabric_dict.get("config"):
                fabric_dict["config"] = json.dumps(fabric_dict.get("config"))

            lists["fabric"] = fabric_dict

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, "Erro cadastrando o Fabric. Erro: %s " % e)

    return render_to_response(templates.FABRIC, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
@csrf_protect
def new_fabric(request, dc_id):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists['dc_id'] = dc_id
        lists["action"] = reverse('fabric.cadastro', args=[dc_id])

        if request.method == 'POST':

            fabric = dict()
            fabric['dc'] = request.META.get('HTTP_REFERER').split("/")[-1]
            fabric['name'] = request.POST.get('fabricname')
            fabric['racks'] = request.POST.get('rack')
            fabric['spines'] = request.POST.get('spn')
            fabric['leafs'] = request.POST.get('lfs')

            newfabric = client.create_apirack().save_fabric(fabric)
            dc_id = newfabric.get('dcroom').get('id')
            lists["dc_id"] = dc_id

            return HttpResponseRedirect(reverse('fabric.ambiente', args=[dc_id]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, "Erro cadastrando o Fabric. Erro: %s " % e)
    return render_to_response(templates.DCROOM_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
@csrf_protect
def fabric_ambiente(request, fabric_id):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists['fabric_id'] = fabric_id
        fabric = client.create_apirack().get_fabric(fabric_id=fabric_id).get("fabric")[0]
        fabric_name = fabric.get("name")
        lists['fabric_name'] = fabric_name
        lists["action"] = reverse('fabric.ambiente', args=[fabric_id])

        if request.method == 'POST':

            envs = list()
            env_oob = dict()
            env_hosts = dict()
            env_hosts_fe = dict()
            env_hosts_boca = dict()
            env_hosts_bocab = dict()
            env_prod_dsr = dict()
            env_prod_dmz = dict()
            env_spn_be = dict()
            env_spn_fe = dict()
            env_spn_bo = dict()
            env_spn_boca = dict()
            env_spn_bocab = dict()
            env_lflf_be = dict()
            env_lflf_fe = dict()
            env_lflf_bo = dict()
            env_lflf_boca = dict()
            env_lflf_bocab = dict()
            env_interno_fe = dict()
            env_interno_be = dict()

            net_type_list = client.create_tipo_rede().listar().get("net_type")
            for type in net_type_list:
                if type.get("name")=="Rede invalida equipamentos":
                    net_type_id = type.get("id")

            configs = list()
            if request.POST.get('ipv4range'):
                v4 = {
                    'subnet': request.POST.get('ipv4range'),
                    'new_prefix': str(request.POST.get('prefixv4')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs.append(v4)
            if request.POST.get('ipv6range'):
                v6 = {
                    'subnet': request.POST.get('ipv6range'),
                    'new_prefix': str(request.POST.get('prefixv6')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs.append(v6)

            configs_lf = list()
            if request.POST.get('ipv4rangelflf'):
                v4 = {
                    'subnet': request.POST.get('ipv4rangelflf'),
                    'new_prefix': str(request.POST.get('prefixv4lflf')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_lf.append(v4)
            if request.POST.get('ipv6rangelflf'):
                v6 = {
                    'subnet': request.POST.get('ipv6rangelflf'),
                    'new_prefix': str(request.POST.get('prefixv6lflf')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_lf.append(v6)

            configs_int = list()
            if request.POST.get('ipv4rangeint'):
                v4_int = {
                    'subnet': request.POST.get('ipv4rangeint'),
                    'new_prefix': str(request.POST.get('prefixv4int')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_int.append(v4_int)
            if request.POST.get('ipv6rangeint'):
                v6_int = {
                    'subnet': request.POST.get('ipv6rangeint'),
                    'new_prefix': str(request.POST.get('prefixv6int')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_int.append(v6_int)

            configs_int_fe = list()
            if request.POST.get('ipv4rangeintfe'):
                v4_int_fe = {
                    'subnet': request.POST.get('ipv4rangeintfe'),
                    'new_prefix': str(request.POST.get('prefixv4intfe')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_int_fe.append(v4_int_fe)
            if request.POST.get('ipv6rangeintfe'):
                v6_int_Fe = {
                    'subnet': request.POST.get('ipv6rangeintfe'),
                    'new_prefix': str(request.POST.get('prefixv6intfe')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_int_fe.append(v6_int_Fe)

            configs_dsr = list()
            if request.POST.get('ipv4rangeintbodsr'):
                v4_dsr = {
                    'subnet': request.POST.get('ipv4rangeintbodsr'),
                    'new_prefix': str(request.POST.get('prefixv4intbodsr')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_dsr.append(v4_dsr)
            if request.POST.get('ipv6rangeintbodsr'):
                v6_dsr = {
                    'subnet': request.POST.get('ipv6rangeintbodsr'),
                    'new_prefix': str(request.POST.get('prefixv6intbodsr')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_dsr.append(v6_dsr)

            configs_dmz = list()
            if request.POST.get('ipv4rangeintbodmz'):
                v4_dmz = {
                    'subnet': request.POST.get('ipv4rangeintbodmz'),
                    'new_prefix': str(request.POST.get('prefixv4intbodmz')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_dmz.append(v4_dmz)
            if request.POST.get('ipv6rangeintbodmz'):
                v6_dmz = {
                    'subnet': request.POST.get('ipv6rangeintbodmz'),
                    'new_prefix': str(request.POST.get('prefixv6intbodmz')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_dmz.append(v6_dmz)

            configs_ca_a = list()
            if request.POST.get('ipv4rangeintbo_a_'):
                v4_int_ca_a = {
                    'subnet': request.POST.get('ipv4rangeintbo_a_'),
                    'new_prefix': str(request.POST.get('prefixv4inboa')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_ca_a.append(v4_int_ca_a)
            if request.POST.get('ipv6rangeintbo_a_'):
                v6_int_ca_a = {
                    'subnet': request.POST.get('ipv6rangeintbo_a_'),
                    'new_prefix': str(request.POST.get('prefixv6intbo_a_')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_ca_a.append(v6_int_ca_a)

            configs_ca_b = list()
            if request.POST.get('ipv4rangeintbo_b_'):
                v4_int_ca_b = {
                    'subnet': request.POST.get('ipv4rangeintbo_b_'),
                    'new_prefix': str(request.POST.get('prefixv4intbob')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_ca_b.append(v4_int_ca_b)
            if request.POST.get('ipv6rangeintbo_b_'):
                v6_int_ca_b = {
                    'subnet': request.POST.get('ipv6rangeintbo_b_'),
                    'new_prefix': str(request.POST.get('prefixv6intbo_b_')),
                    'type': "v6",
                    'network_type': int(net_type_id),
                }
                configs_ca_b.append(v6_int_ca_b)

            configs_oob = list()
            if request.POST.get('ipv4rangeoob'):
                v4_oob = {
                    'subnet': request.POST.get('ipv4rangeoob'),
                    'new_prefix': str(request.POST.get('prefixv4oob')),
                    'type': "v4",
                    'network_type': int(net_type_id),
                }
                configs_oob.append(v4_oob)



            try:
                env_l3_id = client.create_grupo_l3().inserir(fabric_name).get("logical_environment").get("id")
            except:
                env_l3 = client.create_grupo_l3().listar().get("group_l3")
                for l3 in env_l3:
                    if l3.get("nome")==fabric_name:
                        env_l3_id = l3.get("id")

            env_logic = client.create_ambiente_logico().listar().get("logical_environment")
            for el in env_logic:
                if el.get("nome")=="SPINES":
                    logic_id_spn = el.get("id")
                elif el.get("nome")=="PRODUCAO":
                    logic_id_host = el.get("id")
                elif el.get("nome")=="GERENCIA":
                    logic_id_ger = el.get("id")
                elif el.get("nome")=="INTERNO-RACK":
                    logic_id_int = el.get("id")
                elif el.get("nome")=="LEAF-LEAF":
                    logic_id_lflf = el.get("id")

            vrfs = client.create_api_vrf().search()['vrfs']
            for vrf in vrfs:
                if vrf.get("vrf")=="BEVrf":
                    vrf_id_be = vrf.get("id")
                    vrf_be = vrf.get("vrf")
                elif vrf.get("vrf")=="FEVrf":
                    vrf_id_fe = vrf.get("id")
                    vrf_fe = vrf.get("vrf")
                elif vrf.get("vrf")=="BordaVrf":
                    vrf_id_bo = vrf.get("id")
                    vrf_bo = vrf.get("vrf")
                elif vrf.get("vrf")=="BordaCachosVrf":
                    vrf_id_boca = vrf.get("id")
                    vrf_boca = vrf.get("vrf")
                elif vrf.get("vrf")=="BordaCachosBVrf":
                    vrf_id_bocab = vrf.get("id")
                    vrf_bocab = vrf.get("vrf")
                elif vrf.get("vrf")=="Default":
                    vrf_id = vrf.get("id")
                    vrf_ = vrf.get("vrf")

            details_hosts = list()
            details_hosts_be = {
                'min_num_vlan_1': int(request.POST.get('vlanminintbe')) if request.POST.get('vlanminintbe') else None,
                'max_num_vlan_1': int(request.POST.get('vlanmaxintbe')) if request.POST.get('vlanmaxintbe') else None,
                'config': [
                    {
                        'subnet': request.POST.get('ipv4rangeint'),
                        'type': "v4",
                        'new_prefix': str(request.POST.get('newprefix_bebe_v4')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv4intbe'))
                    },
                    {
                        'subnet': request.POST.get('ipv6rangeint'),
                        'type': "v6",
                        'new_prefix': str(request.POST.get('newprefix_bebe_v6')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv6intbe'))
                    }
                ],
                'name': "BEBE"
            }
            details_hosts.append(details_hosts_be)

            details_hosts_fe = {
                'min_num_vlan_1': int(request.POST.get('vlanminintbefe')) if request.POST.get('vlanminintbefe') else None,
                'max_num_vlan_1': int(request.POST.get('vlanmaxintbefe')) if request.POST.get('vlanmaxintbefe') else None,
                'config': [
                    {
                        'subnet': request.POST.get('ipv4rangeint'),
                        'type': "v4",
                        'new_prefix': str(request.POST.get('newprefix_befe_v4')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv4intbefe'))
                    },
                    {
                        'subnet': request.POST.get('ipv6rangeint'),
                        'type': "v6",
                        'new_prefix': str(request.POST.get('newprefix_befe_v6')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv6intbefe'))
                    }
                ],
                'name': "BEFE"
            }
            details_hosts.append(details_hosts_fe)

            details_hosts_bo = {
                'min_num_vlan_1': int(request.POST.get('vlanminintbebo')) if request.POST.get('vlanminintbebo') else None,
                'max_num_vlan_1': int(request.POST.get('vlanmaxintbebo')) if request.POST.get('vlanmaxintbebo') else None,
                'config': [
                    {
                        'subnet': request.POST.get('ipv4rangeint'),
                        'type': "v4",
                        'new_prefix': str(request.POST.get('newprefix_bebo_v4')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv4intbebo'))
                    },
                    {
                        'subnet': request.POST.get('ipv6rangeint'),
                        'type': "v6",
                        'new_prefix': str(request.POST.get('newprefix_bebo_v6')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv6intbebo'))
                    }
                ],
                'name': "BEBO"
            }
            details_hosts.append(details_hosts_bo)

            details_hosts_ca = {
                'min_num_vlan_1': int(request.POST.get('vlanminintbeca')) if request.POST.get('vlanminintbeca') else None,
                'max_num_vlan_1': int(request.POST.get('vlanmaxintbeca')) if request.POST.get('vlanmaxintbeca') else None,
                'config': [
                    {
                        'subnet': request.POST.get('ipv4rangeint'),
                        'type': "v4",
                        'new_prefix': str(request.POST.get('newprefix_beca_v4')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv4intbeca'))
                    },
                    {
                        'subnet': request.POST.get('ipv6rangeint'),
                        'type': "v6",
                        'new_prefix': str(request.POST.get('prefixv6intbeca')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('newprefix_beca_v6'))
                    }
                ],
                'name': "BECA"
            }
            details_hosts.append(details_hosts_ca)

            details_hosts_acs = {
                'min_num_vlan_1': int(request.POST.get('vlanminintacs')) if request.POST.get('vlanminintacs') else None,
                'max_num_vlan_1': int(request.POST.get('vlanmaxintacs')) if request.POST.get('vlanmaxintacs') else None,
                'config': [
                    {
                        'subnet': request.POST.get('ipv4rangeint'),
                        'type': "v4",
                        'new_prefix': str(request.POST.get('newprefix_acs_v4')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv4intasc'))
                    },
                    {
                        'subnet': request.POST.get('ipv6rangeint'),
                        'type': "v6",
                        'new_prefix': str(request.POST.get('newprefix_acs_v6')),
                        'network_type': int(net_type_id),
                        'mask': str(request.POST.get('prefixv6intacs'))
                    }
                ],
                'name': "Hosts-ACS"
            }
            details_hosts.append(details_hosts_acs)

            details_fe = {
                'v4': {
                    'new_prefix': str(request.POST.get('newprefix_fe'))
                },
                'v6': {
                    'new_prefix': str(request.POST.get('newprefix_fe_v6'))
                }
            }

            details_dsr = {
                'v4': {
                    'new_prefix': str(request.POST.get('newprefix_dsr'))
                },
                'v6': {
                    'new_prefix': str(request.POST.get('newprefix_dsr_v6'))
                }
            }

            details_ca = {
                'v4': {
                    'new_prefix': str(request.POST.get('newprefix_caa'))
                },
                'v6': {
                    'new_prefix': str(request.POST.get('newprefix_caa_v6'))
                }
            }

            details_cab = {
                'v4': {
                    'new_prefix': str(request.POST.get('newprefix_cab'))
                },
                'v6': {
                    'new_prefix': str(request.POST.get('newprefix_cab_v6'))
                }
            }

            env_dc = client.create_divisao_dc().listar().get("division_dc")
            for dc in env_dc:
                if dc.get("nome")=="BE":
                    env_spn_be["dc_id"] = dc.get("id")
                    env_spn_be["logic_id"] = logic_id_spn
                    env_spn_be["vrf"] = vrf_be
                    env_spn_be["vrf_id"] = vrf_id_be
                    env_spn_be["vlan_min"] = int(request.POST.get('vlanminspnbe')) if request.POST.get('vlanminspnbe') else None
                    env_spn_be["vlan_max"] = int(request.POST.get('vlanmaxspnbe')) if request.POST.get('vlanmaxspnbe') else None
                    env_spn_be["config"] = configs
                    env_lflf_be["dc_id"] = dc.get("id")
                    env_lflf_be["logic_id"] = logic_id_lflf
                    env_lflf_be["vrf"] = vrf_be
                    env_lflf_be["vrf_id"] = vrf_id_be
                    env_lflf_be["vlan_min"] = int(request.POST.get('vlanminlflfbe')) if request.POST.get('vlanminlflfbe') else None
                    env_lflf_be["vlan_max"] = int(request.POST.get('vlanminlflfbe'))+1 if request.POST.get('vlanminlflfbe') else None
                    env_lflf_be["config"] = configs_lf
                    env_hosts["dc_id"] = dc.get("id")
                    env_hosts["logic_id"] = logic_id_host
                    env_hosts["vrf"] = vrf_be
                    env_hosts["vrf_id"] = vrf_id_be
                    env_hosts["vlan_min"] = int(request.POST.get('vlanminintbe')) if request.POST.get('vlanminintbe') else None
                    env_hosts["vlan_max"] = int(request.POST.get('vlanmaxintbe')) if request.POST.get('vlanmaxintbe') else None
                    env_hosts["config"] = configs_int
                    env_hosts["details"] = details_hosts
                    env_interno_be["dc_id"] = dc.get("id")
                    env_interno_be["logic_id"] = logic_id_int
                    env_interno_be["vrf"] = vrf_be
                    env_interno_be["vrf_id"] = vrf_id_be
                    env_interno_be["vlan_min"] = None
                    env_interno_be["vlan_max"] = None
                    env_interno_be["config"] = []
                    envs.append(env_spn_be)
                    envs.append(env_lflf_be)
                    envs.append(env_hosts)
                    envs.append(env_interno_be)
                elif dc.get("nome")=="FE":
                    env_spn_fe["dc_id"] = dc.get("id")
                    env_spn_fe["logic_id"] = logic_id_spn
                    env_spn_fe["vrf"] = vrf_fe
                    env_spn_fe["vrf_id"] = vrf_id_fe
                    env_spn_fe["vlan_min"] = int(request.POST.get('vlanminspnfe')) if request.POST.get('vlanminspnfe') else None
                    env_spn_fe["vlan_max"] = int(request.POST.get('vlanmaxspnfe')) if request.POST.get('vlanmaxspnfe') else None
                    env_spn_fe["config"] = configs
                    env_lflf_fe["dc_id"] = dc.get("id")
                    env_lflf_fe["logic_id"] = logic_id_lflf
                    env_lflf_fe["vrf"] = vrf_fe
                    env_lflf_fe["vrf_id"] = vrf_id_fe
                    env_lflf_fe["vlan_min"] = int(request.POST.get('vlanminlflffe')) if request.POST.get('vlanminlflffe') else None
                    env_lflf_fe["vlan_max"] = int(request.POST.get('vlanminlflffe'))+1 if request.POST.get('vlanminlflffe') else None
                    env_lflf_fe["config"] = configs_lf
                    env_hosts_fe["dc_id"] = dc.get("id")
                    env_hosts_fe["logic_id"] = logic_id_host
                    env_hosts_fe["vrf"] = vrf_fe
                    env_hosts_fe["vrf_id"] = vrf_id_fe
                    env_hosts_fe["vlan_min"] = int(request.POST.get('vlanminint_fe')) if request.POST.get('vlanminint_fe') else None
                    env_hosts_fe["vlan_max"] = int(request.POST.get('vlanmaxint_Fe')) if request.POST.get('vlanmaxint_Fe') else None
                    env_hosts_fe["config"] = configs_int_fe
                    env_hosts_fe["details"] = [details_fe]
                    env_interno_fe["dc_id"] = dc.get("id")
                    env_interno_fe["logic_id"] = logic_id_int
                    env_interno_fe["vrf"] = vrf_fe
                    env_interno_fe["vrf_id"] = vrf_id_fe
                    env_interno_fe["vlan_min"] = None
                    env_interno_fe["vlan_max"] = None
                    env_interno_fe["config"] = []
                    envs.append(env_spn_fe)
                    envs.append(env_lflf_fe)
                    envs.append(env_hosts_fe)
                    envs.append(env_interno_fe)
                elif dc.get("nome")=="BO":
                    env_spn_bo["dc_id"] = dc.get("id")
                    env_spn_bo["logic_id"] = logic_id_spn
                    env_spn_bo["vrf"] = vrf_bo
                    env_spn_bo["vrf_id"] = vrf_id_bo
                    env_spn_bo["vlan_min"] = int(request.POST.get('vlanminspnbo')) if request.POST.get('vlanminspnbo') else None
                    env_spn_bo["vlan_max"] = int(request.POST.get('vlanmaxspnbo')) if request.POST.get('vlanmaxspnbo') else None
                    env_spn_bo["config"] = configs
                    envs.append(env_spn_bo)
                    env_lflf_bo["dc_id"] = dc.get("id")
                    env_lflf_bo["logic_id"] = logic_id_lflf
                    env_lflf_bo["vrf"] = vrf_bo
                    env_lflf_bo["vrf_id"] = vrf_id_bo
                    env_lflf_bo["vlan_min"] = int(request.POST.get('vlanminlflfbo')) if request.POST.get('vlanminlflfbo') else None
                    env_lflf_bo["vlan_max"] = int(request.POST.get('vlanminlflfbo'))+1 if request.POST.get('vlanminlflfbo') else None
                    env_lflf_bo["config"] = configs_lf
                    envs.append(env_lflf_bo)
                elif dc.get("nome")=="BO_DSR":
                    env_prod_dsr["dc_id"] = dc.get("id")
                    env_prod_dsr["logic_id"] = logic_id_host
                    env_prod_dsr["vrf"] = vrf_bo
                    env_prod_dsr["vrf_id"] = vrf_id_bo
                    env_prod_dsr["vlan_min"] = int(request.POST.get('vlanminint_dsr')) if request.POST.get('vlanminint_dsr') else None
                    env_prod_dsr["vlan_max"] = int(request.POST.get('vlanmaxint_dsr')) if request.POST.get('vlanmaxint_dsr') else None
                    env_prod_dsr["config"] = configs_dsr
                    env_prod_dsr["details"] = [details_dsr]
                    envs.append(env_prod_dsr)
                elif dc.get("nome")=="BO_DMZ":
                    env_prod_dmz["dc_id"] = dc.get("id")
                    env_prod_dmz["logic_id"] = logic_id_host
                    env_prod_dmz["vrf"] = vrf_bo
                    env_prod_dmz["vrf_id"] = vrf_id_bo
                    env_prod_dmz["vlan_min"] = int(request.POST.get('vlanminint_dmz')) if request.POST.get('vlanminint_dmz') else None
                    env_prod_dmz["vlan_max"] = int(request.POST.get('vlanmaxint_dmz')) if request.POST.get('vlanmaxint_dmz') else None
                    env_prod_dmz["config"] = configs_dmz
                    envs.append(env_prod_dmz)
                elif dc.get("nome")=="BOCACHOS-A":
                    env_spn_boca["dc_id"] = dc.get("id")
                    env_spn_boca["logic_id"] = logic_id_spn
                    env_spn_boca["vrf"] = vrf_boca
                    env_spn_boca["vrf_id"] = vrf_id_boca
                    env_spn_boca["vlan_min"] = int(request.POST.get('vlanminspnboca')) if request.POST.get('vlanminspnboca') else None
                    env_spn_boca["vlan_max"] = int(request.POST.get('vlanmaxspnboca')) if request.POST.get('vlanmaxspnboca') else None
                    env_spn_boca["config"] = configs
                    envs.append(env_spn_boca)
                    env_lflf_boca["dc_id"] = dc.get("id")
                    env_lflf_boca["logic_id"] = logic_id_lflf
                    env_lflf_boca["vrf"] = vrf_boca
                    env_lflf_boca["vrf_id"] = vrf_id_boca
                    env_lflf_boca["vlan_min"] = int(request.POST.get('vlanminlflfboca')) if request.POST.get('vlanminlflfboca') else None
                    env_lflf_boca["vlan_max"] = int(request.POST.get('vlanminlflfboca'))+1 if request.POST.get('vlanminlflfboca') else None
                    env_lflf_boca["config"] = configs_lf
                    envs.append(env_lflf_boca)
                    env_hosts_boca["dc_id"] = dc.get("id")
                    env_hosts_boca["logic_id"] = logic_id_host
                    env_hosts_boca["vrf"] = vrf_boca
                    env_hosts_boca["vrf_id"] = vrf_id_boca
                    env_hosts_boca["vlan_min"] = int(request.POST.get('vlanminint_a_')) if request.POST.get('vlanminint_a_') else None
                    env_hosts_boca["vlan_max"] = int(request.POST.get('vlanmaxint_a_')) if request.POST.get('vlanmaxint_a_') else None
                    env_hosts_boca["config"] = configs_ca_a
                    env_hosts_boca["details"] = [details_ca]
                    envs.append(env_hosts_boca)
                elif dc.get("nome")=="BOCACHOS-B":
                    env_spn_bocab["dc_id"] = dc.get("id")
                    env_spn_bocab["logic_id"] = logic_id_spn
                    env_spn_bocab["vrf"] = vrf_bocab
                    env_spn_bocab["vrf_id"] = vrf_id_bocab
                    env_spn_bocab["vlan_min"] = int(request.POST.get('vlanminspnbocab')) if request.POST.get('vlanminspnbocab') else None
                    env_spn_bocab["vlan_max"] = int(request.POST.get('vlanmaxspnbocab')) if request.POST.get('vlanmaxspnbocab') else None
                    env_spn_bocab["config"] = configs
                    envs.append(env_spn_bocab)
                    env_lflf_bocab["dc_id"] = dc.get("id")
                    env_lflf_bocab["logic_id"] = logic_id_lflf
                    env_lflf_bocab["vrf"] = vrf_bocab
                    env_lflf_bocab["vrf_id"] = vrf_id_bocab
                    env_lflf_bocab["vlan_min"] = int(request.POST.get('vlanminlflfbocab')) if request.POST.get('vlanminlflfbocab') else None
                    env_lflf_bocab["vlan_max"] = int(request.POST.get('vlanminlflfbocab'))+1 if request.POST.get('vlanminlflfbocab') else None
                    env_lflf_bocab["config"] = configs_lf
                    envs.append(env_lflf_bocab)
                    env_hosts_bocab["dc_id"] = dc.get("id")
                    env_hosts_bocab["logic_id"] = logic_id_host
                    env_hosts_bocab["vrf"] = vrf_boca
                    env_hosts_bocab["vrf_id"] = vrf_id_bocab
                    env_hosts_bocab["vlan_min"] = int(request.POST.get('vlanminint_b_')) if request.POST.get('vlanminint_b_') else None
                    env_hosts_bocab["vlan_max"] = int(request.POST.get('vlanmaxint_b_')) if request.POST.get('vlanmaxint_b_') else None
                    env_hosts_bocab["config"] = configs_ca_b
                    env_hosts_bocab["details"] = [details_cab]
                    envs.append(env_hosts_bocab)
                elif dc.get("nome")=="OOB":
                    env_oob["dc_id"] = dc.get("id")
                    env_oob["logic_id"] = logic_id_ger
                    env_oob["vrf"] = vrf_
                    env_oob["vrf_id"] = vrf_id
                    env_oob["vlan_min"] = int(request.POST.get('vlanminoob')) if request.POST.get('vlanminoob') else None
                    env_oob["vlan_max"] = int(request.POST.get('vlanmaxoob')) if request.POST.get('vlanmaxoob') else None
                    env_oob["config"] = configs_oob
                    envs.append(env_oob)

            url = request.META.get('HTTP_REFERER').split("/")
            fabric_id = url[-1] if url[-1] else url[-2]
            lists["fabric_id"] = fabric_id

            for amb in envs:
                ambiente = {
                    "id": None,
                    "fabric_id": int(fabric_id),
                    "grupo_l3": int(env_l3_id),
                    "ambiente_logico": int(amb.get("logic_id")),
                    "divisao_dc": int(amb.get("dc_id")),
                    "filter": None,
                    "acl_path": None,
                    "ipv4_template": None,
                    "ipv6_template": None,
                    "link": None,
                    "min_num_vlan_1": amb.get("vlan_min"),
                    "max_num_vlan_1": amb.get("vlan_max"),
                    "min_num_vlan_2": None,
                    "max_num_vlan_2": None,
                    "default_vrf": amb.get("vrf_id"),
                    'vrf': amb.get("vrf"),
                    "father_environment": None,
                    "configs": amb.get("config")
                }

                amb_id = client.create_api_environment().create_environment(ambiente)

                environment = dict()
                environment["id"] = amb_id[0].get("id")
                environment["details"] = amb.get("details") if amb.get("details") else []

                fabric = dict()
                config = dict()
                config["Ambiente"] = environment
                fabric["flag"] = True
                fabric["config"] = config

                environment = client.create_apirack().put_fabric(fabric_id, fabric)

            return HttpResponseRedirect(reverse('fabric.bgp', args=[fabric_id]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, "Houve algum problema ao alocar os ambientes do Fabric. "
                                                      "Erro: %s" % e)
        return HttpResponseRedirect(reverse('fabric.ambiente', args=[fabric_id]))

    return render_to_response(templates.DCROOM_ENV_FORM, lists, context_instance=RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}, ])
@csrf_protect
def fabric_bgp(request, fabric_id):

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists = dict()
        lists['fabric_id'] = fabric_id
        lists["action"] = reverse('fabric.bgp', args=[fabric_id])


        if request.method == 'POST':
            lists["fabric_id"] = fabric_id

            bgp = {
                'mpls': "65000",
                'spines': request.POST.get('fabricasnspn'),
                'leafs': request.POST.get('fabricasnlfs')
            }
            vlt = {
                'id_vlt_lf1': request.POST.get('fabricvlt01'),
                'priority_vlt_lf1': request.POST.get('fabricpriority01'),
                'id_vlt_lf2': request.POST.get('fabricvlt02'),
                'priority_vlt_lf2': request.POST.get('fabricpriority02')
            }
            channel = {
                'channel': request.POST.get('channel')
            }
            telecom = {
                'rede': request.POST.get('gerenciatelecom'),
                'vlan': request.POST.get('gerenciavlan')
            }
            monitoracao = {
                'rede': request.POST.get('gerenciamonitoracao'),
                'vlan': request.POST.get('gerenciamonitvlan')
            }
            noc = {
                'rede': request.POST.get('gerencianoc'),
                'vlan': request.POST.get('gerencianocvlan')
            }
            gerencia = {
                'telecom': telecom
            }
            config = {
                'BGP': bgp,
                'Gerencia': gerencia,
                'VLT': vlt,
                'Channel': channel
            }
            fabric = {
                'flag': True,
                'config': config
            }

            environment = client.create_apirack().put_fabric(fabric_id, fabric)

            return HttpResponseRedirect(reverse('fabric', args=[fabric_id]))

    except NetworkAPIClientError as e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, "Erro salvando a configuração do Fabric. Erro: %s" % e)
        return render_to_response(templates.DCROOM_BGP_FORM, lists, context_instance=RequestContext(request))

    return render_to_response(templates.DCROOM_BGP_FORM, lists, context_instance=RequestContext(request))

@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def remove_fabric(request, fabric_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    try:
        client.create_apirack().delete_fabric(fabric_id)
        messages.add_message(request, messages.SUCCESS, "A sala do datacenter foi removida com sucesso.")
    except NetworkAPIClientError as e:
        messages.add_message(request, messages.ERROR, "Não foi possivel remover a sala de datacenter. Erro: %s" % e)
    finally:
        return HttpResponseRedirect(reverse("listdc"))
