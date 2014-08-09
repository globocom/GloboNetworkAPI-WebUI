# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
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
            if back is None or front is None:
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

    return {
        'combo': combo,
        'name': interf['interface'],
        'description': interf['descricao'],
        'protected': prot,
        'equip_name': interf['equipamento_nome'],
        'equip_id': interf['equipamento'],
        'inter_id': interf['id']}


def next_interface(interface, interfs, last_id, first_time):

    front = interface['ligacao_front']
    back = interface['ligacao_back']

    if not front is None and last_id != front:
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


def make_initials_and_params(interfs):
    initials = []
    params = []
    equip_types = []
    up_list = []
    down_list = []
    front_or_back = []

    # First interface to show in edit form
    interface = find_first_interface(interfs)

    # Connect lines
    front = interface['ligacao_front']
    back = interface['ligacao_back']
    e_type = interface['tipo_equip']
    if e_type == str(PATCH_PANEL_ID):
        up, down = 2, 2
        if front is None and not back is None:
            down = 1
            front_or_back.append("front")
        elif back is None and not front is None:
            down = 1
            front_or_back.append("back")

        if len(front_or_back) == 0:
            front_or_back.append("front")
    else:
        up, down = 0, 2
        if not front is None:
            down = 1

    # Add
    brand = interface['marca'] if interface['tipo_equip'] != "2" else "0"
    params.append(brand)
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

        if interface is not None:
            # Connect lines
            front = interface['ligacao_front']
            back = interface['ligacao_back']
            e_type = interface['tipo_equip']
            if e_type == str(PATCH_PANEL_ID):
                up, down = 1, 1
                if not front == last_id or not back == last_id:
                    if front is None or back is None:
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
    return initials, params, equip_types, up_list, down_list, front_or_back
