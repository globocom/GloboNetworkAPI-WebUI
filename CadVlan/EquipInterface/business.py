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
        
        interf['connect'] = 0
        
        front = interf['ligacao_front']
        if front == None or front == "":
            interf['connect'] = 1
            
        if interf['tipo_equip'] == str(PATCH_PANEL_ID):
            back = interf['ligacao_back']
            if back == None or back == "":
                if front == None or front == "":
                    interf['connect'] = 2
                else:
                    interf['connect'] = 1
                possible_firsts.append(interf)
        else:
            possible_firsts.append(interf)
            
    # Order by id
    sorted_list = sorted(possible_firsts, key=itemgetter('id'))
    
    # Get first
    return sorted_list[0]

def get_initial(interf):
    if interf['marca'] == "3":
        combo = interf['interface'][0:2] if not interf['interface'].startswith("Serial") else "Serial"
    else:
        combo = ""
        
    prot = 0
    if interf['protegida'] == "1":
        prot = 1
        
    return {'combo': combo, 'name': interf['interface'], 'description': interf['descricao'], 
            'protected': prot, 'equip_name': interf['equipamento_nome'],
            'equip_id': interf['equipamento'], 'inter_id': interf['id']}

def next_interface(interface, interfs, last_id):
    front = interface['ligacao_front']
    back = interface['ligacao_back']
    
    if (not front == None or not front == "") and (last_id != front):
        return get_id_in_list(interfs, front), interface['id']
    else:
        return get_id_in_list(interfs, back), interface['id']

def make_initials_and_params(interfs):
    initials = []
    params = []
    equip_types = []
    connects = []
    
    # First interface to show in edit form
    interface = find_first_interface(interfs)
    # Add
    initials.append(get_initial(interface))
    params.append(interface['marca'])
    equip_types.append(interface['tipo_equip'])
    connects.append(interface['connect'])
    
    last_id = interface['id']
    while True:
        # Get the next interface to show in edit form
        interface, last_id = next_interface(interface, interfs, last_id)
        
        if interface != None:
            # Add
            initials.append(get_initial(interface))
            params.append(interface['marca'])
            equip_types.append(interface['tipo_equip'])
            connects.append(interface['connect'])
        else:
            break
        
    return initials, params, equip_types, connects