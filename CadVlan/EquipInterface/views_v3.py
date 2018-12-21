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
from django.http import HttpResponseRedirect
from CadVlan.Util.Decorators import has_perm
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from CadVlan.Auth.AuthSession import AuthSession
from CadVlan.EquipInterface import facade
from CadVlan.EquipInterface.forms import ConnectFormV3
from CadVlan.messages import equip_interface_messages
from CadVlan.messages import error_messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.templates import ADD_EQUIPMENT_INTERFACE
from CadVlan.templates import AJAX_LIST_INTERFACES
from CadVlan.templates import EDIT_CHANNEL
from CadVlan.templates import EDIT_EQUIPMENT_INTERFACE
from CadVlan.templates import LIST_EQUIPMENT_INTERFACES
from CadVlan.templates import NEW_CHANNEL
from CadVlan.templates import NEW_INTERFACE_CONNECT_FORM
from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required
from CadVlan.Util.shortcuts import render_to_response_ajax

from networkapiclient.exception import NetworkAPIClientError

logger = logging.getLogger('networkapiclient')


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_interface(request, equipment=None):

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

    lists = {
        'environments': equips.get('environments'),
        'equip_name': equips.get('name'),
        'equip_id': equips.get('id')
    }

    data = {
        "start_record": 0,
        "end_record": 1000,
        "asorting_cols": ["id"],
        "searchable_columns": ["nome"],
        "custom_search": "",
        "extends_search": []
    }

    try:
        types = client.create_api_interface_request().get_interface_type(search=data)
        type_list = types.get('interfaces_type')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        return HttpResponseRedirect(url)

    lists['type_list'] = type_list

    if request.method == "POST":

        interface = {
            'interface': request.POST.get('name'),
            'description': request.POST.get('description'),
            'protected': True if int(request.POST.get('protected')) else False,
            'native_vlan': request.POST.get('vlan_nativa'),
            'type': int(request.POST.get('access')),
            'equipment': int(equips.get('id'))
        }

        try:
            interface_obj = client.create_api_interface_request().create([interface])
            interface_id = interface_obj.get('interfaces')[0].get('id')
            messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return render_to_response(ADD_EQUIPMENT_INTERFACE, lists, RequestContext(request))

        data["end_record"] = 30000
        data["asorting_cols"] = []
        data["searchable_columns"] = []

        envs = client.create_api_environment().search(fields=["name", "id"], search=data)

        try:
            for e, v in zip(request.POST.getlist('environment'), request.POST.getlist('rangevlan')):
                for obj in envs.get('environments'):
                    if obj.get('name') in e:
                        int_env_map = dict(interface=int(interface_id),
                                           environment=int(obj.get('id')),
                                           range_vlans=v)
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

                search_equipment = client.create_api_equipment(
                    ).search(
                        fields=['id', 'name'],
                        search=data
                    )

                equipments = search_equipment.get('equipments')

                for equip in equipments:
                    if str(equip.get('name')).upper() == str(search_form).upper():
                        data["searchable_columns"] = ["equipamento__id"]
                        data["custom_search"] = equip.get('id')

                        search_interface = client.create_api_interface_request().search(
                            fields=['id',
                                    'interface',
                                    'equipment__details',
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
                                         'Equipamento não tem interfaces associadas.')

                lists['equip_interface'] = interface_list
                lists['search_form'] = search_form
                lists['interface_flag'] = interface_flag
                lists['equip_id'] = equipments[0].get('id')

        return render_to_response(
                LIST_EQUIPMENT_INTERFACES,
                lists,
                RequestContext(request)
            )

    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(
                LIST_EQUIPMENT_INTERFACES,
                lists,
                RequestContext(request)
            )
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return render_to_response(
                LIST_EQUIPMENT_INTERFACES,
                lists,
                RequestContext(request)
            )


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_interface(request, interface_id=None):
    auth = AuthSession(request.session)
    equip_interface = auth.get_clientFactory().create_api_interface_request()

    try:
        equip_interface.remove([interface_id])
        messages.add_message(
                request,
                messages.SUCCESS,
                equip_interface_messages.get("success_remove")
            )

    except NetworkAPIClientError, e:
        message = str(
                error_messages.get("can_not_remove_error")
            ) + " " + str(e)
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
def server_edit_interface(request, interface=None):

    if request.method == "POST":

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        try:
            interface_obj = client.create_api_interface_request().get(ids=[interface])
            interface = interface_obj.get('interfaces')[0]
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.WARNING, 'Erro ao buscar interface id %s.' % interface)

        interface_dict = interface
        interface_dict["interface"] = request.POST.get('sw_interface_name')
        interface_dict["description"] = request.POST.get('sw_int_desc')

        try:
            client.create_api_interface_request().update([interface_dict])
            messages.add_message(request, messages.SUCCESS, 'Interface atualizada com sucesso.')
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
        except Exception, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse("edit.channel", args=[interface.get('channel')]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def basic_edit_interface(request, interface=None):

    if request.method == "POST":

        auth = AuthSession(request.session)
        client = auth.get_clientFactory()

        try:
            interface_obj = client.create_api_interface_request().get(ids=[interface])
            interface = interface_obj.get('interfaces')[0]
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.WARNING, 'Erro ao buscar interface id %s.' % interface)

        interface_dict = interface
        interface_dict["interface"] = request.POST.get('sw_interface_name')
        interface_dict["description"] = request.POST.get('sw_int_desc')

        try:
            client.create_api_interface_request().update([interface_dict])
            messages.add_message(request, messages.SUCCESS, 'Interface atualizada com sucesso.')
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
        except Exception, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect(reverse("edit.channel", args=[interface.get('channel')]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def edit_interface_get(request, interface=None):

    lists = {}

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
        lists["equip_name"] = equipment_name
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

    try:
        first_item, last_item, interface_map = facade.get_interface_map(request, client, interface)
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
def edit_interface_post(request, interface=None):

    lists = {}

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
        lists["equip_name"] = equipment_name
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
        trunk = False

        int_type = None
        for tipo in type_list:
            if str(tipo.get('type')).lower() == str(request.POST.get('type')).lower():
                int_type = tipo.get('id')
                if str(tipo.get('type')).lower() == "trunk":
                    trunk = True

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
                              type=int(int_type),
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

        if int_envs:
            try:
                for env in int_envs:
                    client.create_api_interface_request().disassociate_interface_environments([env.get('id')])
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, 'Erro ao remover os ambientes associados anteriormente.')

        if trunk:
            data = dict()
            data["start_record"] = 0
            data["end_record"] = 30000
            data["asorting_cols"] = []
            data["searchable_columns"] = []
            data["custom_search"] = ""
            data["extends_search"] = []

            envs = client.create_api_environment().search(fields=["name", "id"], search=data)

            try:
                for e, v in zip(request.POST.getlist('environmentCh' + str(interface)),
                                request.POST.getlist('rangevlanCh' + str(interface))):
                    for obj in envs.get('environments'):
                        if obj.get('name') in e:
                            int_env_map = dict(interface=int(interface),
                                               environment=int(obj.get('id')),
                                               range_vlans=v)
                            client.create_api_interface_request().associate_interface_environments([int_env_map])
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, 'Erro ao atualizar os ambientes.')

    try:
        first_item, last_item, interface_map = facade.get_interface_map(request, client, interface)
        lists['interface_map'] = facade.get_ordered_list(first_item, last_item, interface_map)
        lists['total_itens'] = last_item - first_item
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Não foi possível montar o map da interface.')

    url_list = '/interface/?search_equipment=%s' % equipment.get('name')
    url_edit = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse(url_list)

    return HttpResponseRedirect(url_edit)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def connect_interfaces(request, id_interface=None, front_or_back=None, all_interfaces=None):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    lists = dict()
    lists['id_interface'] = id_interface
    lists['front_or_back'] = front_or_back

    if request.method == "GET":

        if request.GET.__contains__('search_equip'):
            equipment_name = request.GET.get('search_equip')
            logger.debug(equipment_name)
        else:
            try:
                int(all_interfaces)
                return render_to_response(NEW_INTERFACE_CONNECT_FORM, lists, RequestContext(request))
            except Exception:
                equipment_name = all_interfaces

        data = dict()
        data["start_record"] = 0
        data["end_record"] = 1000
        data["asorting_cols"] = ["id"]
        data["searchable_columns"] = ["nome"]
        data["custom_search"] = equipment_name
        data["extends_search"] = []

        equipment = list()

        try:
            search_equipment = client.create_api_equipment().search(search=data)
            equipment = search_equipment.get('equipments')

        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
        except Exception, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)

        interface_list = list()

        for equip in equipment:

            data["searchable_columns"] = [""]
            data["custom_search"] = ""
            data["extends_search"] = [{'equipamento__id': equip.get('id')}]

            try:
                search_interface = client.create_api_interface_request().search(
                    fields=['id',
                            'interface',
                            'front_interface__basic',
                            'back_interface__basic'],
                    search=data)

                interface_list = search_interface.get('interfaces')
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

        if not interface_list:
            logger.error('Equipment do not have interfaces availables.')
            messages.add_message(request, messages.ERROR, 'Equipment do not have interfaces availables.')
            return render_to_response(NEW_INTERFACE_CONNECT_FORM, lists, RequestContext(request))

        try:
            int(front_or_back)
            for i in interface_list:
                if front_or_back and i.get('front_interface') or not front_or_back and i.get('back_interface'):
                    interface_list.remove(i)

            lists['connect_form'] = ConnectFormV3(equipment[0],
                                                  interface_list,
                                                  initial={'equip_name': equipment[0].get('name'),
                                                           'equip_id': equipment[0].get('id')})
            lists['equipment'] = equipment[0]

        except Exception:
                if all_interfaces:
                    allInt = list()
                    for i in interface_list:
                        allInt.append({'id': i.get('id'), 'interface': i.get('interface')})
                    lists['all_interfaces'] = allInt

                    return render_to_response_ajax(AJAX_LIST_INTERFACES,
                                                   lists,
                                                   context_instance=RequestContext(request))

    elif request.method == "POST":

        equip_id = request.POST['equip_id']

        search_equipment = client.create_api_equipment().get([equip_id])
        equipment = search_equipment.get('equipments')

        interface_list = list()

        data = dict()
        data["start_record"] = 0
        data["end_record"] = 1000
        data["asorting_cols"] = ["id"]
        data["searchable_columns"] = [""]
        data["custom_search"] = ""

        for equip in equipment:

            data["extends_search"] = [{'equipamento__id': equip.get('id')}]

            try:
                search_interface = client.create_api_interface_request().search(
                    fields=['id',
                            'interface',
                            'front_interface__basic',
                            'back_interface__basic'],
                    search=data)

                interface_list = search_interface.get('interfaces')

            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, e)

        for i in interface_list:
            if front_or_back and i.get('front_interface') or not front_or_back and i.get('back_interface'):
                interface_list.remove(i)

        form = ConnectFormV3(equipment[0],
                             interface_list,
                             request.POST)

        if form.is_valid():

            front = form.cleaned_data['front']
            back = form.cleaned_data['back']

            link_a = "front" if front_or_back else "back"
            interface_a = dict(link=link_a, id=id_interface)

            if front:
                interface_b = dict(link="front", id=front)
            else:
                interface_b = dict(link="back", id=back)

            try:
                client.create_api_interface_request().connecting_interfaces([interface_a, interface_b])
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_connect"))
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, 'Erro linkando as interfaces: %s' % e)
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.ERROR, 'Erro linkando as interfaces: %s' % e)

            response = HttpResponseRedirect(reverse("interface.edit", args=[id_interface]))
            response.status_code = 278

            return response

        else:
            lists['connect_form'] = form
            lists['equipment'] = equipment[0]

    return render_to_response(NEW_INTERFACE_CONNECT_FORM, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def disconnect_interfaces(request, interface_a=None, interface_b=None):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        client.create_api_interface_request().disconnecting_interfaces([interface_a, interface_b])
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
        url_param = reverse("equip.interface.add.channel",
                            args=[equipment_name])
        url_param = url_param + "/?ids=" + interface_id
    else:
        messages.add_message(request, messages.ERROR,
                             "Select an interface.")
        url_param = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')

    return HttpResponseRedirect(url_param)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def add_channel_(request):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    lists = dict()

    if request.method == "POST":

        data = dict()
        data["start_record"] = 0
        data["end_record"] = 30000
        data["asorting_cols"] = []
        data["searchable_columns"] = []
        data["custom_search"] = ""
        data["extends_search"] = []

        envs = client.create_api_environment().search(fields=["name", "id"], search=data)

        env_id = None
        envs_vlans = list()
        for e, v in zip(request.POST.getlist('environment'), request.POST.getlist('rangevlan')):
            for obj in envs.get('environments'):
                if obj.get('name') in e:
                    env_id = obj.get('id')
            if env_id:
                group = dict(env=env_id, vlans=v)
                envs_vlans.append(group)

        channel = {
            'name': request.POST.get('channelnumber'),
            'lacp':  True if int(request.POST.get('lacp_yes')) else False,
            'int_type': "Access" if int(request.POST.get('access')) else "Trunk",
            'vlan': int(request.POST.get('channelvlan')),
            'interfaces': request.POST.getlist('switchInt'),
            'envs_vlans': envs_vlans
        }

        try:
            channel_obj = client.create_api_interface_request().create_channel([channel])
            channel_id = channel_obj[0].get('id')
            messages.add_message(request, messages.SUCCESS, "O channel foi criado com sucesso!")
        except NetworkAPIClientError as e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, "Erro ao criar o channel. %s" % e)
            return render_to_response(NEW_CHANNEL, lists, RequestContext(request))

        return HttpResponseRedirect(reverse("edit.channel", args=[channel_id]))

    return render_to_response(NEW_CHANNEL, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True, "read": True}])
def edit_channel_(request, channel_id=None):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    lists = dict()
    lists['channel_id'] = channel_id

    fields = ['id', 'front_interface__id']

    fields_get = ['id',
                  'interface',
                  'description',
                  'protected',
                  'type__details',
                  'native_vlan',
                  'equipment__basic',
                  'front_interface__basic',
                  'back_interface',
                  'channel__basic']

    search = {
        "start_record": 0,
        "end_record": 50,
        "asorting_cols": [],
        "searchable_columns": ["channel__id"],
        "custom_search": channel_id,
        "extends_search": []
    }

    try:
        sw_ids = []
        server_ids = []
        interfaces = client.create_api_interface_request().search(search=search, fields=fields).get('interfaces')
        for i in interfaces:
            sw_ids.append(i.get('id'))
            server_ids.append(i.get('front_interface'))
        sw_interfaces = client.create_api_interface_request().get(sw_ids, fields=fields_get).get('interfaces')
        server_interfaces = client.create_api_interface_request().get(server_ids, fields=fields_get)
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Erro ao buscar o channel de Id %s.' % channel_id)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

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
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    lists['type_list'] = type_list

    if request.method == "POST":

        lacp = True if int(request.POST.get('lacp')) else False
        protected = True if int(request.POST.get('protected')) else False

        envs_vlans = list()

        if str(request.POST.get('type')).lower() in "Access".lower():
            int_type = "Access"
        else:
            int_type = "Trunk"

            data = dict()
            data["start_record"] = 0
            data["end_record"] = 30000
            data["asorting_cols"] = []
            data["searchable_columns"] = []
            data["custom_search"] = ""
            data["extends_search"] = []

            envs = client.create_api_environment().search(fields=["name", "id"], search=data)

            env_id = None
            for e, v in zip(request.POST.getlist('environment'), request.POST.getlist('rangevlan')):
                for obj in envs.get('environments'):
                    if obj.get('name') in e:
                        env_id = obj.get('id')

                group = dict(env=env_id, vlans=v)
                envs_vlans.append(group)

        channel_obj = dict(
            id=channel_id,
            name=str(request.POST.get('channelnumber')),
            lacp=lacp,
            protected=protected,
            int_type=int_type,
            vlan=int(request.POST.get('vlan_nativa')),
            interfaces=sw_ids,
            envs_vlans=envs_vlans
        )

        try:
            client.create_api_interface_request().update_channel([channel_obj])
            messages.add_message(request, messages.SUCCESS, "O channel foi editado com sucesso!")
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, 'Erro ao atualizar o channel. Error: %s' % e)
            url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
            return HttpResponseRedirect(url)

        try:
            sw_ids = []
            server_ids = []
            interfaces = client.create_api_interface_request().search(search=search, fields=fields).get('interfaces')
            for i in interfaces:
                sw_ids.append(i.get('id'))
                server_ids.append(i.get('front_interface'))
            sw_interfaces = client.create_api_interface_request().get(sw_ids, fields=fields_get).get('interfaces')
            server_interfaces = client.create_api_interface_request().get(server_ids, fields=fields_get)
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.WARNING, 'Erro ao buscar o channel de Id %s.' % channel_id)
            url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
            return HttpResponseRedirect(url)

    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = ["interface__id"]
    data["custom_search"] = str(sw_ids[0])

    try:
        environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                        fields=['environment__basic',
                                                                                                'range_vlans'])
        environments = environments.get('interface_environments')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    try:
        lists['server_map'] = facade.get_environments(client, server_interfaces.get('interfaces'))
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    lists['total_itens'] = len(server_interfaces) - 1

    try:
        sw_int_map, channel_map = facade.get_channel_map(sw_interfaces)
        sw_int_map['environments'] = environments
        lists['channel_map'] = channel_map
        lists['total_channel'] = len(channel_map) - 1
        lists['sw_int_map'] = sw_int_map
        lists['total_sw'] = len(sw_int_map) - 1
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Não foi possível montar o map do channel.')
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    return render_to_response(EDIT_CHANNEL, lists, RequestContext(request))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_channel(request, channel_id=None):
    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        client.create_api_interface_request().remove_channel([channel_id])
        messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_remove_channel"))
    except ValueError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
    except NetworkAPIClientError, e:
        logger.error(e)
        message = str(
                error_messages.get("can_not_remove_error")
            ) + " " + str(e)
        messages.add_message(request, messages.ERROR, message)
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)

    url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')

    return HttpResponseRedirect(url)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def dissociate_channel_interface(request, channel_id, interface_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    fields_get = ['id',
                  'protected',
                  'type__details',
                  'native_vlan',
                  'equipment__details',
                  'front_interface__basic',
                  'back_interface',
                  'channel__basic']

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 50
    data["extends_search"] = []
    data["asorting_cols"] = []
    data["searchable_columns"] = ["channel__id"]
    data["custom_search"] = channel_id

    try:
        sw_ids = list()
        interfaces = client.create_api_interface_request().search(search=data, fields=fields_get).get('interfaces')
        interface_obj = interfaces[0]
        for i in interfaces:
            sw_ids.append(int(i.get('id')))
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Erro ao buscar o channel de Id %s.' % channel_id)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    sw_ids.remove(int(interface_id))

    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = ["interface__id"]
    data["custom_search"] = str(sw_ids[0])

    try:
        environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                        fields=['environment__basic',
                                                                                                'range_vlans'])
        environments = environments.get('interface_environments')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    envs_vlans = list()

    for obj in environments:
        group = dict(env=obj.get('environment').get('id'), vlans=obj.get('range_vlans'))
        envs_vlans.append(group)

    channel_obj = dict(
        id=channel_id,
        name=interface_obj.get('channel').get('name'),
        lacp=interface_obj.get('channel').get('lacp'),
        protected=interface_obj.get('protected'),
        int_type=interface_obj.get('type').get('type'),
        vlan=interface_obj.get('native_vlan'),
        interfaces=sw_ids,
        envs_vlans=envs_vlans
    )

    try:
        client.create_api_interface_request().update_channel([channel_obj])
        messages.add_message(request, messages.SUCCESS, "Interface foi removida do channel com sucesso.")
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, "Erro ao retirar a interface do channel. Err: " + " " + str(e))
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse("edit.channel", args=[channel_id]))


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def associate_channel_interface(request, channel_id):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    fields_get = ['id',
                  'protected',
                  'type__details',
                  'native_vlan',
                  'equipment__details',
                  'front_interface__basic',
                  'back_interface',
                  'channel__basic']

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 50
    data["extends_search"] = []
    data["asorting_cols"] = []
    data["searchable_columns"] = ["channel__id"]
    data["custom_search"] = channel_id

    try:
        sw_ids = list()
        interfaces = client.create_api_interface_request().search(search=data, fields=fields_get).get('interfaces')
        interface_obj = interfaces[0]
        for i in interfaces:
            sw_ids.append(int(i.get('id')))
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Erro ao buscar o channel de Id %s.' % channel_id)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    interface_id = request.POST.get('switchInt')
    sw_ids.append(int(interface_id))

    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = ["interface__id"]
    data["custom_search"] = str(sw_ids[0])

    try:
        environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                        fields=['environment__basic',
                                                                                                'range_vlans'])
        environments = environments.get('interface_environments')
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, 'Erro ao buscar os tipos de interface. Error: %s' % e)
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    envs_vlans = list()

    for obj in environments:
        group = dict(env=obj.get('environment').get('id'), vlans=obj.get('range_vlans'))
        envs_vlans.append(group)

    channel_obj = dict(
        id=channel_id,
        name=interface_obj.get('channel').get('name'),
        lacp=interface_obj.get('channel').get('lacp'),
        protected=interface_obj.get('protected'),
        int_type=interface_obj.get('type').get('type'),
        vlan=interface_obj.get('native_vlan'),
        interfaces=sw_ids,
        envs_vlans=envs_vlans
    )

    try:
        client.create_api_interface_request().update_channel([channel_obj])
        messages.add_message(request, messages.SUCCESS, "Interface foi adicionada ao channel com sucesso.")
    except NetworkAPIClientError, e:
        logger.error(str(e))
        messages.add_message(request, messages.ERROR, "Erro ao adicionar interface ao channel. Err: "
                             + " " + str(e))
        url = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else reverse('interface.list')
        return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse("edit.channel", args=[channel_id]))
