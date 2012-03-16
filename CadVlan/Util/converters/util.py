# -*- coding:utf-8 -*-
'''
Created on 06/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

def split_to_array(string, sep = ";"):
    """
    Returns an array of strings separated by regex
    """
    if string is not None:
        return string.split(sep)

def replace_id_to_name(main_list, type_list, str_main_id, str_type_id, str_prop):
    """
    Return list replacing type id to type name
    """
    
    for item in main_list:
        id_type = item[str_main_id]
        for type_item in type_list:
            if type_item[str_type_id] == id_type:
                item[str_main_id] = type_item[str_prop]
                break
    
    return main_list