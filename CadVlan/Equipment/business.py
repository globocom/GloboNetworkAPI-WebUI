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

@cache_function(CACHE_EQUIPMENTS_TIMEOUT)
def cache_list_equipment_all(equipment):
    equipments = equipment.get_all()
    return equipments["equipamentos"]

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

def list_users(user):
    users = user.listar()
    ulist = dict()
    ulist["list_from_model"] = users["usuario"]
    user_list = []

    for list in ulist["list_from_model"]:
        user_list.append(str(list['nome']) + ' - ' + str(list['user']))
        
    ulist['list'] = user_list
    return ulist