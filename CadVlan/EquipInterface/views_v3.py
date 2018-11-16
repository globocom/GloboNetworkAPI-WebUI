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
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'protected': True if int(request.POST.get('protected')) else False,
            'vlan': int(request.POST.get('vlan_nativa')),
            'type': int_type,
            'equipment_id': int(equip_id)
        }

        try:
            interface_obj = client.create_api_interface_request().create([interface])
            interface_id = interface_obj.get('interfaces')[0].get('id')
            messages.add_message(request, messages.SUCCESS, equip_interface_messages.get("success_insert"))
        except NetworkAPIClientError, e:
            logger.error(e)
            messages.add_message(request, messages.ERROR, e)
            return render_to_response(ADD_EQUIPMENT_INTERFACE, lists, context_instance=RequestContext(request))

        environments = request.POST.getlist('environments')

        if environments:
            try:
                for env in environments:
                    client.create_interface().associar_ambiente(env, interface_id)
            except NetworkAPIClientError, e:
                logger.error(e)
                messages.add_message(request, messages.WARNING, 'Os ambientes não foram associados à interface')

        return HttpResponseRedirect('/interface/?search_equipment=%s' % equips.get('name'))

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
