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

logger = logging.getLogger(__name__)


def get_interface_map(request, client, interface):
    interface_map = dict()
    item = 100

    fields = ['id',
              'interface',
              'equipment__details',
              'channel',
              'front_interface',
              'back_interface',
              'description',
              'protected',
              'type__details',
              'native_vlan']

    response = client.create_api_interface_request().get(ids=[interface], fields=fields)
    interface_obj = response.get('interfaces')[0]

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 1000
    data["asorting_cols"] = ["id"]
    data["extends_search"] = []
    data["searchable_columns"] = ["interface__id"]
    data["custom_search"] = str(interface)

    envs = list()

    try:
        environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                        fields=['environment__basic',
                                                                                                'range_vlans'])
        envs = environments.get('interface_environments')
    except Exception, e:
        logger.error(e)
        messages.add_message(request, messages.WARNING, 'Erro ao buscar os ambientes associados a interface. '
                                                        'Error: %s' % e)

    interface_obj['environments'] = envs

    interface_map[str(item)] = interface_obj
    main_interface = interface_obj
    prior_interface = interface_obj.get('id')

    if interface_obj.get('front_interface'):

        next_interface = interface_obj.get('front_interface')

        while next_interface:

            item += 1
            response = client.create_api_interface_request().get(ids=[next_interface], fields=fields)
            interface_obj = response.get('interfaces')[0]

            data["searchable_columns"] = ["interface__id"]
            data["custom_search"] = str(interface)

            envs = list()

            try:
                environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                                fields=[
                                                                                                    'environment__basic',
                                                                                                    'range_vlans'])
                envs = environments.get('interface_environments')
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.WARNING, 'Erro ao buscar os ambientes associados a interface. '
                                                                'Error: %s' % e)

            interface_obj['environments'] = envs

            interface_map[str(item)] = interface_obj
            interface_map[str(item - 1)]['next_interface'] = interface_obj.get('id')

            if interface_obj.get('back_interface') == prior_interface:
                next_interface = interface_obj.get('front_interface') if interface_obj.get('front_interface') else None
            elif interface_obj.get('front_interface') == prior_interface:
                next_interface = interface_obj.get('back_interface') if interface_obj.get('back_interface') else None
            else:
                next_interface = None

            prior_interface = interface_obj.get('id')

    last = item
    item = 100
    prior_interface = main_interface.get('id')

    if main_interface.get('back_interface'):

        next_interface = main_interface.get('back_interface')

        while next_interface:

            item -= 1
            response = client.create_api_interface_request().get(ids=[next_interface], fields=fields)
            interface_obj = response.get('interfaces')[0]

            data["searchable_columns"] = ["interface__id"]
            data["custom_search"] = str(interface)

            envs = list()

            try:
                environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                                fields=[
                                                                                                    'environment__basic',
                                                                                                    'range_vlans'])
                envs = environments.get('interface_environments')
            except Exception, e:
                logger.error(e)
                messages.add_message(request, messages.WARNING, 'Erro ao buscar os ambientes associados a interface. '
                                                                'Error: %s' % e)

            interface_obj['environments'] = envs

            interface_map[str(item)] = interface_obj
            interface_map[str(item)]['next_interface'] = interface_map[str(item + 1)].get('id')

            if interface_obj.get('back_interface') == prior_interface:
                next_interface = interface_obj.get('front_interface') if interface_obj.get('front_interface') else None
            elif interface_obj.get('front_interface') == prior_interface:
                next_interface = interface_obj.get('back_interface') if interface_obj.get('back_interface') else None
            else:
                next_interface = None

            prior_interface = interface_obj.get('id')

    first = item

    return first, last, interface_map


def get_channel_map(interfaces):

    sw_interfaces = list()
    i = dict()

    for i in interfaces:
        sw_int_obj = dict(
            id=i.get('id'),
            channel=i.get('channel').get('id'),
            equip_name=i.get('equipment').get('name'),
            interface_name=i.get('interface'),
            description=i.get('description'),
            server_name=i.get('front_interface').get('equipment').get('name'),
            server_interface_id=i.get('front_interface').get('id'),
            server_interface_name=i.get('front_interface').get('interface')
        )
        sw_interfaces.append(sw_int_obj)

    return i, sw_interfaces


def get_ordered_list(first, last, interface_map):
    interface_list = list()

    for j in range(first, last + 1):
        interface_list.append(interface_map.get(str(j)))

    return interface_list


def get_environments(client, interfaces):

    data = dict()
    data["start_record"] = 0
    data["end_record"] = 1000
    data["extends_search"] = []
    data["asorting_cols"] = ["id"]
    data["searchable_columns"] = ["interface__id"]

    for i in interfaces:
        data["custom_search"] = str(i.get('id'))
        environments = client.create_api_interface_request().get_interface_environments(search=data,
                                                                                        fields=['environment__basic',
                                                                                                'range_vlans'])
        i['environments'] = environments.get('interface_environments')

    return interfaces