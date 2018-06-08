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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from CadVlan.Util.Decorators import has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.EquipInterface import facade
from CadVlan.messages import equip_interface_messages
from CadVlan.messages import error_messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.templates import ADD_EQUIPMENT_INTERFACE
from CadVlan.templates import EDIT_EQUIPMENT_INTERFACE
from CadVlan.templates import LIST_EQUIPMENT_INTERFACES
from CadVlan.templates import NEW_INTERFACE_CONNECT_FORM
from CadVlan.EquipInterface.forms import ConnectForm
from CadVlan.forms import SearchEquipForm

from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required

from networkapiclient.exception import NetworkAPIClientError

logger = logging.getLogger(__name__)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_interface(request, equipment=None):
    lists = dict()

    # Get user
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()
    url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')

    try:
        search_equipment = client.create_api_equipment().get(ids=[equipment],
                                                             kind='details',
                                                             fields=['id', 'name', 'environments'])
        equips = search_equipment.get('equipments')[0]
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return HttpResponseRedirect(url)

    lists['environments'] = equips.get('environments')
    lists['equip_name'] = equips.get('name')
    equip_id = equips.get('id')
    lists['equip_id'] = equip_id

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 1000
    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = ["nome"]
    data["custom_search"] = ""
    data["extends_search"] = []

    try:
        types = client.create_api_interface_request().get_interface_type(search=data)
        type_list = types.get('interfaces_type')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        return HttpResponseRedirect(url)

    lists['type_list'] = type_list

    if request.method == "POST":

        int_type = int(request.POST.get('type'))

        interface = {
            'interface': request.POST.get('name'),
            'description': request.POST.get('description'),
            'protected': True if int(request.POST.get('protected')) else False,
            'native_vlan': request.POST.get('vlan_nativa'),
            'type': int_type,
            'equipment': int(equip_id)
        }

        try:
            interface_obj = client.create_api_interface_request().create([interface])
            interface_id = interface_obj.get('interfaces')[0].get('id')
            messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return render_to_response(ADD_EQUIPMENT_INTERFACE, lists, RequestContext(request))

        environments = request.POST.getlist('environments')

        if environments:
            try:
                for env in environments:
                    int_env_map = dict(interface=int(interface_id),
                                       environment=int(env),
                                       range_vlans=request.POST.get('vlans'))
                    client.create_api_interface_request().associate_interface_environments([int_env_map])
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.WARNING, 'Os ambientes não foram associados à interface.')

        return HttpResponseRedirect('/interface/?search_equipment=%s' % equips.get('name'))

    return render_to_response(ADD_EQUIPMENT_INTERFACE, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "read": True}])
def list_equipment_interfaces(request):
    lists = dict()
    interface_list = list()

    try:

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        interface_flag = False

        if request.method == "GET":

            if request.GET.__contains__('search_equipment'):

                search_form = request.GET.get('search_equipment')

                data = dict()
                data["start_record"] = 0
                data["end_record"] = 1000
                data["asorting_cols"] = ["id"]
                data["searchable_columns"] = ["nome"]
                data["custom_search"] = search_form
                data["extends_search"] = []

                search_equipment = client.create_api_equipment().search(fields=['id',
                                                                                'name'],
                                                                        search=data)

                equipments = search_equipment.get('equipments')

                for equip in equipments:
                    if str(equip.get('name')).upper() == str(search_form).upper():
                        data["searchable_columns"] = ["equipamento__id"]
                        data["custom_search"] = equip.get('id')

                        search_interface = client.create_api_interface_request().search(
                            fields=['id',
                                    'interface',
                                    'equipment__basic',
                                    'native_vlan',
                                    'type__details',
                                    'channel__basic',
                                    'front_interface__basic',
                                    'back_interface__basic'],
                            search=data)
                        interface_list = search_interface.get('interfaces')
                        interface_flag = True

                if not equipments:
                    raise Exception('Equipamento não encontrado.')

                if not interface_list:
                    messages.add_message(request,
                                         messages.WARNING,
                                         str(interface_list))

                lists['equip_interface'] = interface_list
                lists['search_form'] = search_form
                lists['interface_flag'] = interface_flag
                lists['equip_id'] = equipments[0].get('id')

        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(LIST_EQUIPMENT_INTERFACES, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_interface(request, interface_id=None):
    auth = AuthSession(request.session)
    equip_interface = auth.get_clientFactory().create_api_interface_request()

    try:
        equip_interface.remove([interface_id])
        messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_remove"))

    except NetworkAPIClientError, e:
        message = str(error_messages.get("can_not_remove_error")) + " " + str(e)
        logger.error(e)
        messages.add_message(request, messages.WARNING, message)
    except ValueError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
    return HttpResponseRedirect(url)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def edit_interface(request, interface=None):
    lists = dict()

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    fields = ['id',
              'equipment__details',
              'front_interface',
              'back_interface']

    equipment_name = ""

    try:
        interface_obj = client.create_api_interface_request().get(ids=[interface], fields=fields)
        interfaces = interface_obj.get('interfaces')[0]
        equipment = interfaces.get('equipment')
        equipment_name = equipment.get('name')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Erro ao buscar interface %s.' % interface)
        return HttpResponseRedirect('/interface/?search_equipment=%s' % equipment_name)

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 1000
    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = ["nome"]
    data["custom_search"] = ""
    data["extends_search"] = []

    try:
        types = client.create_api_interface_request().get_interface_type(search=data)
        type_list = types.get('interfaces_type')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        return HttpResponseRedirect('/interface/?search_equipment=%s' % equipment.get('name'))

    lists['type_list'] = type_list

    if request.method == "POST":

        data["searchable_columns"] = ["interface__id"]
        data["custom_search"] = str(interface)

        int_envs = list()

        try:
            int_envs = client.create_api_interface_request().get_interface_environments(search=data)
            int_envs = int_envs.get('interface_environments')
        except Exception, e:
            logger.error(e)
            messages.add_message(request, messages.WARNING, 'Erro ao buscar os ambientes associados a interface. '
                                                            'Error: %s' % e)

        interface_dict = dict(id=int(interfaces.get('id')),
                              interface=request.POST.get('name'),
                              description=request.POST.get('description'),
                              protected=True if int(request.POST.get('protected')) else False,
                              native_vlan=request.POST.get('vlan_nativa'),
                              type=int(request.POST.get('type')),
                              equipment=int(equipment.get('id')),
                              front_interface=interfaces.get('front_interface'),
                              back_interface=interfaces.get('back_interface'))

        try:
            client.create_api_interface_request().update([interface_dict])
            messages.add_message(request, messages.SUCCESS, 'Interface atualizada com sucesso.')
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
        except Exception, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

        environments = request.POST.getlist('environments')

        if int_envs:
            try:
                for env in int_envs:
                    client.create_api_interface_request().disassociate_interface_environments([env.get('id')])
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, 'Erro ao remover os ambientes associados anteriormente.')

        if environments:
            try:
                for env in environments:
                    int_env_map = dict(interface=int(interface),
                                       environment=int(env),
                                       range_vlans=request.POST.get('vlans'))
                    client.create_api_interface_request().associate_interface_environments([int_env_map])
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, 'Erro ao atualizar os ambientes.')

    try:
        first_item, last_item, interface_map = facade.get_interface_map(client, interface)
        lists['interface_map'] = facade.get_ordered_list(first_item, last_item, interface_map)
        lists['total_itens'] = last_item - first_item
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Não foi possível montar o map da interface.')
        return HttpResponseRedirect('/interface/?search_equipment=%s' % equipment.get('name'))

    return render_to_response(EDIT_EQUIPMENT_INTERFACE, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def connect_interfaces(request, id_interface=None, front_or_back=None):
    lists = dict()

    if not (front_or_back == "0" or front_or_back == "1"):
        raise Http404

    try:

        # Get user
        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        lists['id_interface'] = id_interface
        lists['front_or_back'] = front_or_back
        lists['search_form'] = SearchEquipForm()

        if request.method == "GET":

            if request.GET.__contains__('equip_name'):

                lists['search_form'] = search_form = SearchEquipForm(
                    request.GET)

                if search_form.is_valid():

                    # Get equip name in form
                    name_equip = search_form.cleaned_data['equip_name']

                    # Get equipment by name from NetworkAPI
                    equipment = client.create_equipamento().listar_por_nome(
                        name_equip)['equipamento']
                    # Get interfaces related to equipment selected
                    interf_list = client.create_interface().list_all_by_equip(
                        equipment['id'])

                    # Remove interface that is being added to the combobox
                    i = []
                    for inter in interf_list['interfaces']:

                        if id_interface != inter['id']:
                            i.append(inter)

                    interf_list = dict()
                    interf_list['interfaces'] = i

                    lists['connect_form'] = ConnectForm(equipment, interf_list['interfaces'], initial={
                        'equip_name': equipment['nome'], 'equip_id': equipment['id']})
                    lists['equipment'] = equipment

        elif request.method == "POST":
            equip_id = request.POST['equip_id']

            # Get equipment by name from NetworkAPI
            equipment = client.create_equipamento().listar_por_id(
                equip_id)['equipamento']
            # Get interfaces related to equipment selected
            interf_list = client.create_interface().list_all_by_equip(
                equipment['id'])

            form = ConnectForm(
                equipment, interf_list['interfaces'], request.POST)

            if form.is_valid():

                front = form.cleaned_data['front']
                back = form.cleaned_data['back']

                # Get interface to link
                interface_client = client.create_interface()
                interface = interface_client.get_by_id(id_interface)
                interface = interface.get("interface")
                if interface['protegida'] == "True":
                    interface['protegida'] = 1
                else:
                    interface['protegida'] = 0

                if len(front) > 0:
                    # Get front interface selected
                    inter_front = interface_client.get_by_id(front)
                    inter_front = inter_front.get("interface")
                    if inter_front['protegida'] == "True":
                        inter_front['protegida'] = 1
                    else:
                        inter_front['protegida'] = 0

                    related_list = client.create_interface().list_connections(
                        inter_front["interface"], inter_front["equipamento"])
                    for i in related_list.get('interfaces'):

                        if i['equipamento'] == interface['equipamento']:
                            lists['connect_form'] = form
                            lists['equipment'] = equipment
                            raise Exception(
                                'Configuração inválida. Loop detectado nas ligações entre patch-panels')

                    # Business Rules
                    interface_client.alterar(inter_front['id'], inter_front['interface'], inter_front['protegida'],
                                             inter_front['descricao'], interface['id'], inter_front['ligacao_back'],
                                             inter_front['tipo'], inter_front['vlan'])
                    if front_or_back == "0":
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], interface['ligacao_front'],
                                                 inter_front['id'],
                                                 interface['tipo'], interface['vlan'])
                    else:
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], inter_front['id'],
                                                 interface['ligacao_back'],
                                                 interface['tipo'], interface['vlan'])

                else:
                    # Get back interface selected
                    inter_back = interface_client.get_by_id(back)
                    inter_back = inter_back.get("interface")
                    if inter_back['protegida'] == "True":
                        inter_back['protegida'] = 1
                    else:
                        inter_back['protegida'] = 0

                    related_list = client.create_interface().list_connections(inter_back["interface"],
                                                                              inter_back["equipamento"])

                    for i in related_list.get('interfaces'):
                        if i['equipamento'] == interface['equipamento']:
                            lists['connect_form'] = form
                            lists['equipment'] = equipment
                            raise Exception('Configuração inválida. Loop detectado nas ligações entre patch-panels')

                    # Business Rules
                    interface_client.alterar(inter_back['id'], inter_back['interface'], inter_back['protegida'],
                                             inter_back['descricao'], inter_back['ligacao_front'], interface['id'],
                                             inter_back['tipo'], inter_back['vlan'])
                    if front_or_back == "0":
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], interface['ligacao_front'],
                                                 inter_back['id'],
                                                 interface['tipo'], interface['vlan'])
                    else:
                        interface_client.alterar(interface['id'], interface['interface'], interface['protegida'],
                                                 interface['descricao'], inter_back['id'],
                                                 interface['ligacao_back'],
                                                 interface['tipo'], interface['vlan'])

                messages.add_message(
                    request, messages.SUCCESS, equip_interface_messages.get("success_connect"))

                url_param = reverse(
                    "equip.interface.edit.form", args=[interface['equipamento_nome'], id_interface])
                response = HttpResponseRedirect(url_param)
                response.status_code = 278

                return response

            else:
                lists['connect_form'] = form
                lists['equipment'] = equipment

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return render_to_response(NEW_INTERFACE_CONNECT_FORM, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def disconnect_interfaces(request, interface_a=None, interface_b=None):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        interface_obj = client.create_api_interface_request().get(ids=[interface_a])
        interfaces = interface_obj.get('interfaces')[0]
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Erro ao buscar interface %s.' % interface_a)
        return HttpResponseRedirect(reverse("interface.edit", args=[interface_a]))

    interface_dict = dict(id=int(interfaces.get('id')),
                          interface=interfaces.get('interface'),
                          description=interfaces.get('description'),
                          protected=interfaces.get('protected'),
                          native_vlan=interfaces.get('native_vlan'),
                          type=interfaces.get('type'),
                          equipment=interfaces.get('equipment'),
                          front_interface=None if interfaces.get('front_interface') == int(
                              interface_b) else interfaces.get('front_interface'),
                          back_interface=None if interfaces.get('back_interface') == int(
                              interface_b) else interfaces.get('back_interface'))

    try:
        client.create_api_interface_request().update([interface_dict])
        messages.add_message(request, messages.SUCCESS, 'Conexão removida.')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse("interface.edit", args=[interface_a]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_channel(request, interface_id=None):
    ref = request.META.get('HTTP_REFERER').split('=')
    equipment_name = ref[-1]

    if interface_id:
        url_param = reverse("equip.interface.add.channel", args=[equipment_name])
        url_param = url_param + "/?ids=" + interface_id
    else:
        messages.add_message(request, messages.ERROR, "Select an interface.")
        url_param = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')

    return HttpResponseRedirect(url_param)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_channel(request, interface_id=None):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        client.create_interface().delete_channel(interface_id)
        messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_remove_channel"))
    except ValueError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except NetworkAPIClientError, e:
        logger.error(e)
        message = str(error_messages.get("can_not_remove_error")) + " " + str(e)
        messages.add_message(request, messages.ERROR, message)
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
    return HttpResponseRedirect(url)
