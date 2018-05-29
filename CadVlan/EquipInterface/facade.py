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

logger = logging.getLogger(__name__)


def get_interface_map(client, interface):

    interface_map = dict()
    front = False
    back = False
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
    interface_map[str(item)] = interface_obj
    main_interface = interface_obj

    try:
        if interface_obj.get('front_interface'):

            next_interface = interface_obj.get('front_interface')
            front = True

            while next_interface:

                item += 1

                logger.info('loop back: %s' % item)

                response = client.create_api_interface_request().get(ids=[next_interface], fields=fields)
                interface_obj = response.get('interfaces')[0]
                interface_map[str(item)] = interface_obj

                if front and interface_obj.get('back_interface'):
                    next_interface = interface_obj.get('back_interface')
                    front = False
                    back = True
                elif back and interface_obj.get('front_interface'):
                    next_interface = interface_obj.get('front_interface')
                    back = False
                    front = True
                else:
                    next_interface = None

                if next_interface == main_interface.get('id'):
                    next_interface = None

        last = item
        item = 100
    except Exception:
        raise Exception('primeiro')
    try:
        if main_interface.get('back_interface'):

            next_interface = main_interface.get('back_interface')
            back = True

            while next_interface:

                item -= 1
                logger.info('loop back: %s' % item)

                response = client.create_api_interface_request().get(ids=[next_interface], fields=fields)
                interface_obj = response.get('interfaces')[0]
                interface_map[str(item)] = interface_obj

                if front and interface_obj.get('back_interface'):
                    next_interface = interface_obj.get('back_interface')
                    front = False
                    back = True
                elif back and interface_obj.get('front_interface'):
                    next_interface = interface_obj.get('front_interface')
                    back = False
                    front = True
                else:
                    next_interface = None

                if next_interface == main_interface.get('id'):
                    next_interface = None

        first = item
    except Exception:
        raise Exception('segundo')
    return first, last, interface_map


def get_ordered_list(first, last, interface_map):

    interface_list = list()

    for j in range(first, last+1):
        interface_list.append(interface_map.get(str(j)))

    return interface_list