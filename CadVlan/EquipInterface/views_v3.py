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
from CadVlan.messages import equip_interface_messages
from CadVlan.messages import error_messages
from CadVlan.permissions import EQUIPMENT_MANAGEMENT
from CadVlan.templates import ADD_EQUIPMENT_INTERFACE
from CadVlan.templates import LIST_EQUIPMENT_INTERFACES

from CadVlan.Util.Decorators import log
from CadVlan.Util.Decorators import login_required

from networkapiclient.exception import NetworkAPIClientError

from CadVlan.EquipInterface.forms import AddInterfaceForm, AddEnvInterfaceForm


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
        equip = client.create_equipamento().listar_por_nome(str(equipment))
    except NetworkAPIClientError, e:
        logger.error(e)
        messages.add_message(request, messages.ERROR, e)
        return HttpResponseRedirect(url)

    equip = equip.get('equipamento')
    brand = equip['id_marca'] if equip['id_tipo_equipamento'] != "2" else "0"
    int_type_list = client.create_interface().list_all_interface_types()

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 1000
    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = []
    data["custom_search"] = ""
    data["extends_search"] = [{'equipamentoambiente__equipamento': 46033}]

    try:
        envs = client.create_api_environment().search(search=data,
                                                      fields=['id', 'name', 'min_num_vlan_1', 'max_num_vlan_1'])
        lists['environments'] = envs.get('environments')
    except:
        lists['environments'] = list()
        pass

    lists['equip_type'] = equip['id_tipo_equipamento']
    lists['equip_name'] = equip['nome']
    lists['brand'] = brand
    lists['int_type'] = int_type_list
    lists['id'] = None

    if request.method == "GET":
        lists['form'] = AddInterfaceForm(int_type_list,
                                         brand,
                                         0,
                                         initial={'equip_name': equip['nome'],'equip_id': equip['id']})

    if request.method == "POST":

        form = AddInterfaceForm(int_type_list, brand, 0, request.POST)

        try:

            if form.is_valid():

                name = form.cleaned_data['name']
                description = form.cleaned_data['description']
                protected = form.cleaned_data['protected']
                int_type = form.cleaned_data['int_type']
                vlan = form.cleaned_data['vlan']

                # if environment_list is not None and envform.is_valid():
                  #  envs = envform.cleaned_data['environment']

                trunk = 0
                if int_type=="0":
                    int_type = "access"
                else:
                    int_type = "trunk"
                    trunk = 1

                id_int = client.create_interface().inserir(name,
                                                           protected,
                                                           description,
                                                           None,
                                                           None,
                                                           equip['id'],
                                                           int_type,
                                                           vlan)
                messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))

                id_int = id_int.get("interface")

                if trunk and envs is not None:
                    for env in envs:
                        client.create_interface().associar_ambiente(env, id_int['id'])
                    messages.add_message(request,
                                         messages.SUCCESS,
                                         equip_interface_messages.get("success_associando_amb"))

                return HttpResponseRedirect(url)
            else:
                lists['form'] = form

        except NetworkAPIClientError, e:
            logger.error(e)
            lists['form'] = form
            messages.add_message(request, messages.ERROR, e)

    return render_to_response(ADD_EQUIPMENT_INTERFACE, lists, context_instance=RequestContext(request))

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

                if not equipments:
                    raise Exception("Equipment Does Not Exist.")

                if len(equipments) == 1:
                    data["searchable_columns"] = ["equipamento__id"]
                    data["custom_search"] = equipments[0].get('id')
                    search_interface = client.create_api_interface_request(
                        ).search(fields=['id',
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
                    if not interface_list:
                        messages.add_message(
                            request,
                            messages.WARNING,
                            "Equipamento não possui interfaces cadastradas."
                        )

                lists['equip_interface'] = interface_list
                lists['search_form'] = search_form
                lists['interface_flag'] = interface_flag

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

    url = request.META.get('HTTP_REFERER')
    if request.META.get('HTTP_REFERER')
    else reverse('interface.list')

    return HttpResponseRedirect(url)


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
        url_param = request.META.get('HTTP_REFERER')
        if request.META.get('HTTP_REFERER')
        else reverse('interface.list')

    return HttpResponseRedirect(url_param)


@log
@login_required
@has_perm([{"permission": EQUIPMENT_MANAGEMENT, "write": True}])
def delete_channel(request, interface_id=None):

    auth = AuthSession(request.session)
    client = auth.get_clientFactory()

    try:
        client.create_interface().delete_channel(interface_id)
        messages.add_message(
                    request,
                    messages.SUCCESS,
                    equip_interface_messages.get("success_remove_channel")
                )

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

    url = request.META.get('HTTP_REFERER')
    if request.META.get('HTTP_REFERER')
    else reverse('interface.list')

    return HttpResponseRedirect(url)
