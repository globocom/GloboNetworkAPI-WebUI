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

from operator import itemgetter
from CadVlan.settings import PATCH_PANEL_ID
from CadVlan.Util.utility import get_id_in_list


def find_first_interface(interfs):
    """
    Get first interface to show in edit form
    """

    possible_firsts = []

    for interf in interfs:

        if interf['tipo_equip'] == str(PATCH_PANEL_ID):
            back = interf['ligacao_back']
            front = interf['ligacao_front']
            if back == None or front == None:
                possible_firsts.append(interf)
        else:
            possible_firsts.append(interf)

    # If none is possible
    if len(possible_firsts) == 0:
        for interf in interfs:
            possible_firsts.append(interf)

    # Order by id
    sorted_list = sorted(possible_firsts, key=itemgetter('id'))

    # Get first
    return sorted_list[0]


def get_initial(interf):
    if interf['marca'] == "3":
        combo = interf['interface'][0:2] if not interf[
            'interface'].startswith("Serial") else "Serial"
    else:
        combo = ""

    prot = 0
    if interf['protegida'] == u'True':
        prot = 1

    return {'combo': combo, 'name': interf['interface'], 'description': interf['descricao'],
            'protected': prot, 'equip_name': interf['equipamento_nome'],
            'equip_id': interf['equipamento'], 'inter_id': interf['id']}


def next_interface(interface, interfs, last_id, first_time):

    front = interface['ligacao_front']
    back = interface['ligacao_back']

    if not front == None and last_id != front:
        inter_front = get_id_in_list(interfs, front)
        return inter_front, interface['id'], False
    elif last_id != back:
        inter_back = get_id_in_list(interfs, back)
        return inter_back, interface['id'], False
    elif len(interfs) == 2:
        if first_time:
            inter_equal = interfs[1]
            first_time = False
            return inter_equal, inter_equal['id'], False
        else:
            return None, interfs[1]['id'], False
    else:
        return None, interface['id'], False


def make_initials_and_params(interfs, list=None):
    initials = []
    params = []
    equip_types = []
    up_list = []
    down_list = []
    front_or_back = []
    int_type_list = []

    # First interface to show in edit form
    interface = find_first_interface(interfs)

    # Connect lines
    front = interface['ligacao_front']
    back = interface['ligacao_back']
    e_type = interface['tipo_equip']
    if e_type == str(PATCH_PANEL_ID):
        up, down = 2, 2
        if front == None and not back == None:
            down = 1
            front_or_back.append("front")
        elif back == None and not front == None:
            down = 1
            front_or_back.append("back")

        if len(front_or_back) == 0:
            front_or_back.append("front")
    else:
        up, down = 0, 2
        if not front == None:
            down = 1

    # Add
    brand = interface['marca'] if interface['tipo_equip'] != "2" else "0"
    params.append(brand)
    int_type_list.append(list)
    up_list.append(up)
    down_list.append(down)
    initials.append(get_initial(interface))
    equip_types.append(interface['tipo_equip'])

    last_id = interface['id']
    first_time = True
    while True:
        # Get the next interface to show in edit form

        interface, last_id, first_time = next_interface(
            interface, interfs, last_id, first_time)

        if interface != None:
            # Connect lines
            front = interface['ligacao_front']
            back = interface['ligacao_back']
            e_type = interface['tipo_equip']
            if e_type == str(PATCH_PANEL_ID):
                up, down = 1, 1
                if not front == last_id or not back == last_id:
                    if front == None or back == None:
                        down = 2
                if front == last_id:
                    front_or_back.append("front")
                elif back == last_id:
                    front_or_back.append("back")
            else:
                up, down = 1, 0

            # Add
            brand = interface['marca'] if interface[
                'tipo_equip'] != "2" else "0"
            params.append(brand)
            up_list.append(up)
            down_list.append(down)
            initials.append(get_initial(interface))
            equip_types.append(interface['tipo_equip'])
        else:
            break

    # Reverse lists order to call pop method in template
    params.reverse()
    up_list.reverse()
    down_list.reverse()
    equip_types.reverse()
    front_or_back.reverse()
    return initials, params, equip_types, up_list, down_list, front_or_back, int_type_list
