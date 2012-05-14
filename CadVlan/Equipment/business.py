# -*- coding:utf-8 -*-
'''
Created on 01/03/2012
Author: avanzolin / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''
from CadVlan.Util.Decorators import cache_function
from CadVlan.settings import CACHE_EQUIPMENTS_TIMEOUT

@cache_function(CACHE_EQUIPMENTS_TIMEOUT)
def cache_list_equipment(equipment):
    equipments = equipment.list_all()
    elist = dict()
    elist["list"] = equipments["equipamentos"]
    return elist


def get_group_by_id(grupos, id_grupo):
    
    for grupo in grupos:
        if grupo['id'] == id_grupo:
            return grupo
        
    return None

def get_ambiente_by_id(ambientes,id_ambiente):
        
    for ambiente in ambientes:
        if ambiente['id'] == id_ambiente:
            return ambiente
            
    return None